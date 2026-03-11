import logging
import os
import shutil


import aiofiles
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database.database import get_db
from app.models.models import User, Instance, APK
from app.models.schemas import APKResponse, APKListResponse
from app.api.auth import get_current_user
from app.services.instance_manager import InstanceManagerService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/apk", tags=["APK Management"])
settings = get_settings()


@router.post("/upload", response_model=APKResponse, status_code=201)
async def upload_apk(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload an APK file."""
    if not file.filename.endswith(".apk"):
        raise HTTPException(status_code=400, detail="Only .apk files are allowed")

    # Ensure upload directory exists
    os.makedirs(settings.APK_UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(settings.APK_UPLOAD_DIR, f"{current_user.id}_{file.filename}")

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    apk = APK(
        name=file.filename,
        file_path=file_path,
        uploaded_by=current_user.id,
    )
    db.add(apk)
    await db.flush()
    await db.refresh(apk)

    logger.info(f"APK uploaded: {apk.name} by {current_user.email}")
    return apk


@router.get("", response_model=APKListResponse)
async def list_apks(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List all APKs uploaded by the current user."""
    result = await db.execute(select(APK).where(APK.uploaded_by == current_user.id))
    apks = result.scalars().all()
    return APKListResponse(apks=apks, total=len(apks))


@router.post("/{apk_id}/install/{instance_id}")
async def install_apk(
    apk_id: str,
    instance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Install an APK into a running Android instance."""
    # Verify APK ownership
    result = await db.execute(
        select(APK).where(APK.id == apk_id, APK.uploaded_by == current_user.id)
    )
    apk = result.scalar_one_or_none()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    # Verify instance ownership and status
    result = await db.execute(
        select(Instance).where(Instance.id == instance_id, Instance.user_id == current_user.id)
    )
    instance = result.scalar_one_or_none()
    if not instance:
        raise HTTPException(status_code=404, detail="Instance not found")
    if instance.status != "running":
        raise HTTPException(status_code=400, detail="Instance must be running to install APK")

    manager = InstanceManagerService()
    success = await manager.install_apk(instance, apk.file_path)

    if not success:
        raise HTTPException(status_code=500, detail="Failed to install APK")

    logger.info(f"APK {apk.name} installed on {instance.name}")
    return {"message": f"APK {apk.name} installed successfully on {instance.name}"}


@router.delete("/{apk_id}", status_code=204)
async def delete_apk(
    apk_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an uploaded APK."""
    result = await db.execute(
        select(APK).where(APK.id == apk_id, APK.uploaded_by == current_user.id)
    )
    apk = result.scalar_one_or_none()
    if not apk:
        raise HTTPException(status_code=404, detail="APK not found")

    # Remove file
    if os.path.exists(apk.file_path):
        os.remove(apk.file_path)

    await db.delete(apk)
    logger.info(f"APK {apk.name} deleted by {current_user.email}")
