import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.database import get_db
from app.models.models import User, Instance, InstanceStatus
from app.models.schemas import InstanceCreate, InstanceResponse, InstanceListResponse
from app.api.auth import get_current_user
from app.services.instance_manager import InstanceManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/instances", tags=["Instances"])
settings = get_settings()


@router.get("", response_model=InstanceListResponse)
async def list_instances(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all instances belonging to the current user."""
    result = await db.execute(
        select(Instance).where(Instance.user_id == current_user.id)
    )
    instances = result.scalars().all()
    return InstanceListResponse(instances=instances, total=len(instances))


@router.post("/create", response_model=InstanceResponse, status_code=status.HTTP_201_CREATED)
async def create_instance(
    data: InstanceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new Android instance for the current user."""
    # Check instance limit
    count_result = await db.execute(
        select(func.count()).select_from(Instance).where(Instance.user_id == current_user.id)
    )
    current_count = count_result.scalar()
    if current_count >= settings.MAX_INSTANCES_PER_USER:
        raise HTTPException(
            status_code=400,
            detail=f"Maximum {settings.MAX_INSTANCES_PER_USER} instances per user",
        )

    # Allocate unique ports
    manager = InstanceManagerService()
    ports = await manager.allocate_ports(db)

    container_name = f"waydroid-{current_user.id}-{data.name}".replace(" ", "-").lower()

    instance = Instance(
        user_id=current_user.id,
        name=data.name,
        status=InstanceStatus.STOPPED,
        container_name=container_name,
        adb_port=ports["adb_port"],
        stream_port=ports["stream_port"],
    )
    db.add(instance)
    await db.flush()
    await db.refresh(instance)

    logger.info(f"Instance created: {instance.name} for user {current_user.email}")
    return instance


@router.post("/{instance_id}/start", response_model=InstanceResponse)
async def start_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Start an Android instance."""
    instance = await _get_user_instance(instance_id, current_user, db)

    if instance.status == InstanceStatus.RUNNING:
        raise HTTPException(status_code=400, detail="Instance is already running")

    manager = InstanceManagerService()
    instance.status = InstanceStatus.STARTING
    await db.flush()

    success = await manager.start_instance(instance)
    instance.status = InstanceStatus.RUNNING if success else InstanceStatus.ERROR
    await db.flush()
    await db.refresh(instance)

    logger.info(f"Instance {instance.name} status: {instance.status}")
    return instance


@router.post("/{instance_id}/stop", response_model=InstanceResponse)
async def stop_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Stop a running Android instance."""
    instance = await _get_user_instance(instance_id, current_user, db)

    if instance.status == InstanceStatus.STOPPED:
        raise HTTPException(status_code=400, detail="Instance is already stopped")

    manager = InstanceManagerService()
    instance.status = InstanceStatus.STOPPING
    await db.flush()

    success = await manager.stop_instance(instance)
    instance.status = InstanceStatus.STOPPED if success else InstanceStatus.ERROR
    await db.flush()
    await db.refresh(instance)

    logger.info(f"Instance {instance.name} stopped")
    return instance


@router.delete("/{instance_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_instance(
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an Android instance."""
    instance = await _get_user_instance(instance_id, current_user, db)

    if instance.status == InstanceStatus.RUNNING:
        manager = InstanceManagerService()
        await manager.stop_instance(instance)

    manager = InstanceManagerService()
    await manager.destroy_instance(instance)
    await db.delete(instance)

    logger.info(f"Instance {instance.name} deleted by {current_user.email}")


# ──────────────────────────── Helpers ────────────────────────────

async def _get_user_instance(
    instance_id: str, user: User, db: AsyncSession
) -> Instance:
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id, Instance.user_id == user.id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    return instance
