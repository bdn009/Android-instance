import asyncio
import logging
import platform
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.models.models import Instance

import shutil

logger = logging.getLogger(__name__)
settings = get_settings()

# Simulate if waydroid command is not installed (e.g., inside Docker or on Windows)
HAS_WAYDROID = shutil.which("waydroid") is not None


class InstanceManagerService:
    """
    Manages Waydroid Android instance lifecycle.
    On non-Linux systems, operations are simulated for development.
    """

    async def allocate_ports(self, db: AsyncSession) -> dict:
        """Allocate unique ADB and stream ports for a new instance."""
        result = await db.execute(
            select(func.max(Instance.adb_port))
        )
        max_adb = result.scalar() or (settings.WAYDROID_BASE_ADB_PORT - 1)

        result = await db.execute(
            select(func.max(Instance.stream_port))
        )
        max_stream = result.scalar() or (settings.WAYDROID_BASE_STREAM_PORT - 1)

        return {
            "adb_port": max_adb + 1,
            "stream_port": max_stream + 1,
        }

    async def start_instance(self, instance: Instance) -> bool:
        """Start a Waydroid container."""
        logger.info(f"Starting instance: {instance.container_name}")

        if not HAS_WAYDROID:
            logger.warning("Non-Linux host — simulating Waydroid start")
            await asyncio.sleep(1)  # Simulate startup delay
            return True

        try:
            # Initialize the Waydroid container
            proc = await asyncio.create_subprocess_exec(
                "waydroid", "container", "start",
                "--name", instance.container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)

            if proc.returncode != 0:
                logger.error(f"Waydroid start failed: {stderr.decode()}")
                return False

            # Connect ADB
            adb_proc = await asyncio.create_subprocess_exec(
                "adb", "connect", f"localhost:{instance.adb_port}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(adb_proc.communicate(), timeout=15)

            logger.info(f"Instance {instance.container_name} started on ADB port {instance.adb_port}")
            return True

        except asyncio.TimeoutError:
            logger.error(f"Timeout starting instance {instance.container_name}")
            return False
        except Exception as e:
            logger.error(f"Error starting instance: {e}")
            return False

    async def stop_instance(self, instance: Instance) -> bool:
        """Stop a running Waydroid container."""
        logger.info(f"Stopping instance: {instance.container_name}")

        if not HAS_WAYDROID:
            logger.warning("Non-Linux host — simulating Waydroid stop")
            await asyncio.sleep(0.5)
            return True

        try:
            proc = await asyncio.create_subprocess_exec(
                "waydroid", "container", "stop",
                "--name", instance.container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=30)

            if proc.returncode != 0:
                logger.error(f"Waydroid stop failed: {stderr.decode()}")
                return False

            # Disconnect ADB
            adb_proc = await asyncio.create_subprocess_exec(
                "adb", "disconnect", f"localhost:{instance.adb_port}",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await adb_proc.communicate()

            logger.info(f"Instance {instance.container_name} stopped")
            return True

        except Exception as e:
            logger.error(f"Error stopping instance: {e}")
            return False

    async def destroy_instance(self, instance: Instance) -> bool:
        """Destroy a Waydroid container completely."""
        logger.info(f"Destroying instance: {instance.container_name}")

        if not HAS_WAYDROID:
            logger.warning("Non-Linux host — simulating Waydroid destroy")
            return True

        try:
            proc = await asyncio.create_subprocess_exec(
                "waydroid", "container", "destroy",
                "--name", instance.container_name,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=30)
            return proc.returncode == 0

        except Exception as e:
            logger.error(f"Error destroying instance: {e}")
            return False

    async def install_apk(self, instance: Instance, apk_path: str) -> bool:
        """Install an APK into a running instance via ADB."""
        logger.info(f"Installing APK {apk_path} on {instance.container_name}")

        if not HAS_WAYDROID:
            logger.warning("Non-Linux host — simulating APK install")
            await asyncio.sleep(1)
            return True

        try:
            proc = await asyncio.create_subprocess_exec(
                "adb", "-s", f"localhost:{instance.adb_port}",
                "install", "-r", apk_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)

            if proc.returncode != 0:
                logger.error(f"APK install failed: {stderr.decode()}")
                return False

            logger.info(f"APK installed successfully on {instance.container_name}")
            return True

        except Exception as e:
            logger.error(f"Error installing APK: {e}")
            return False

    async def get_screen_data(self, instance: Instance) -> Optional[bytes]:
        """Capture a single screenshot from the instance."""
        if not HAS_WAYDROID:
            return None

        try:
            proc = await asyncio.create_subprocess_exec(
                "adb", "-s", f"localhost:{instance.adb_port}",
                "exec-out", "screencap", "-p",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            return stdout if proc.returncode == 0 else None

        except Exception:
            return None
