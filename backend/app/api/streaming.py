import asyncio
import json
import logging


from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.database import get_db, async_session_factory
from app.models.models import Instance, InstanceStatus
from app.services.instance_manager import InstanceManagerService
from app.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Streaming"])
settings = get_settings()


@router.websocket("/ws/stream/{instance_id}")
async def stream_instance(
    websocket: WebSocket,
    instance_id: str,
    token: str = Query(None),
):
    """
    WebSocket endpoint for streaming Android screen and receiving touch input.

    Protocol:
    - Server sends: binary PNG frames (screen captures)
    - Client sends: JSON touch events { "x": float, "y": float, "action": "tap"|"swipe" }
    """
    await websocket.accept()

    # Verify instance exists and is running
    async with async_session_factory() as db:
        result = await db.execute(
            select(Instance).where(Instance.id == instance_id)
        )
        instance = result.scalar_one_or_none()

        if not instance:
            await websocket.send_json({"error": "Instance not found"})
            await websocket.close()
            return

        if instance.status != InstanceStatus.RUNNING:
            await websocket.send_json({"error": "Instance is not running"})
            await websocket.close()
            return

    manager = InstanceManagerService()
    logger.info(f"Stream connected for instance {instance_id}")

    try:
        while True:
            # Capture and send screen frame
            frame_data = await manager.get_screen_data(instance)

            if frame_data:
                await websocket.send_bytes(frame_data)
            else:
                # Send a placeholder frame indicator for dev mode
                await websocket.send_json({
                    "type": "frame_placeholder",
                    "instance_id": instance_id,
                    "message": "No live frame available (dev mode)",
                })

            # Check for incoming touch events (non-blocking)
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=0.1,
                )
                touch_event = json.loads(data)
                await _handle_touch(instance, touch_event)
            except asyncio.TimeoutError:
                pass  # No input received, continue streaming

            await asyncio.sleep(0.033)  # ~30fps

    except WebSocketDisconnect:
        logger.info(f"Stream disconnected for instance {instance_id}")
    except Exception as e:
        logger.error(f"Stream error for instance {instance_id}: {e}")
        await websocket.close()


async def _handle_touch(instance: Instance, event: dict):
    """Send a touch event to the Android instance via ADB."""
    x = event.get("x", 0)
    y = event.get("y", 0)
    action = event.get("action", "tap")

    logger.debug(f"Touch event on {instance.container_name}: {action} at ({x}, {y})")

    try:
        if action == "tap":
            proc = await asyncio.create_subprocess_exec(
                "adb", "-s", f"localhost:{instance.adb_port}",
                "shell", "input", "tap", str(int(x)), str(int(y)),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=5)
        elif action == "swipe":
            end_x = event.get("end_x", x)
            end_y = event.get("end_y", y)
            duration = event.get("duration", 300)
            proc = await asyncio.create_subprocess_exec(
                "adb", "-s", f"localhost:{instance.adb_port}",
                "shell", "input", "swipe",
                str(int(x)), str(int(y)),
                str(int(end_x)), str(int(end_y)),
                str(int(duration)),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=5)
    except Exception as e:
        logger.error(f"Touch event failed: {e}")


@router.websocket("/ws/updates")
async def live_updates(websocket: WebSocket, token: str = Query(None)):
    """
    WebSocket endpoint for real-time instance status updates.
    Broadcasts status changes to connected dashboard clients.
    """
    await websocket.accept()
    logger.info("Dashboard updates WebSocket connected")

    try:
        while True:
            # Poll instance statuses and send updates
            async with async_session_factory() as db:
                result = await db.execute(select(Instance))
                instances = result.scalars().all()

                updates = [
                    {
                        "id": str(inst.id),
                        "name": inst.name,
                        "status": inst.status.value if hasattr(inst.status, 'value') else inst.status,
                        "adb_port": inst.adb_port,
                        "stream_port": inst.stream_port,
                    }
                    for inst in instances
                ]

                await websocket.send_json({"type": "status_update", "instances": updates})

            await asyncio.sleep(3)  # Poll every 3 seconds

    except WebSocketDisconnect:
        logger.info("Dashboard updates WebSocket disconnected")
    except Exception as e:
        logger.error(f"Updates WebSocket error: {e}")
