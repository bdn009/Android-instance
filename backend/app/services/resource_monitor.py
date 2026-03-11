import asyncio
import logging
import psutil
from typing import Optional

from app.config import get_settings
from app.models.schemas import SystemStats

logger = logging.getLogger(__name__)
settings = get_settings()


class ResourceMonitor:
    """Monitors server resources and provides system statistics."""

    @staticmethod
    def get_system_stats(active_instances: int = 0) -> SystemStats:
        """Get current system resource usage."""
        memory = psutil.virtual_memory()
        return SystemStats(
            cpu_percent=psutil.cpu_percent(interval=0.1),
            memory_percent=memory.percent,
            memory_total_gb=round(memory.total / (1024 ** 3), 2),
            memory_available_gb=round(memory.available / (1024 ** 3), 2),
            active_instances=active_instances,
            max_instances=settings.MAX_INSTANCES_PER_USER * 10,  # Rough system max
        )

    @staticmethod
    def can_start_instance() -> bool:
        """Check if the server has enough resources to start a new instance."""
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory()

        # Require at least 2GB free RAM and CPU below 90%
        has_memory = memory.available > 2 * 1024 ** 3
        has_cpu = cpu < 90.0

        if not has_memory:
            logger.warning(f"Low memory: {memory.available / (1024**3):.2f} GB available")
        if not has_cpu:
            logger.warning(f"High CPU: {cpu:.1f}%")

        return has_memory and has_cpu


class InstanceQueue:
    """Redis-backed queue for instance start requests when resources are tight."""

    def __init__(self, redis_client):
        self.redis = redis_client
        self.queue_key = "instance:start_queue"

    async def enqueue(self, instance_id: str):
        """Add an instance start request to the queue."""
        await self.redis.rpush(self.queue_key, instance_id)
        logger.info(f"Queued instance start: {instance_id}")

    async def dequeue(self) -> Optional[str]:
        """Get the next instance to start."""
        result = await self.redis.lpop(self.queue_key)
        return result.decode() if result else None

    async def queue_size(self) -> int:
        """Get number of pending start requests."""
        return await self.redis.llen(self.queue_key)

    async def set_instance_state(self, instance_id: str, state: str):
        """Cache instance state in Redis for fast lookups."""
        await self.redis.set(f"instance:state:{instance_id}", state, ex=300)

    async def get_instance_state(self, instance_id: str) -> Optional[str]:
        """Get cached instance state from Redis."""
        result = await self.redis.get(f"instance:state:{instance_id}")
        return result.decode() if result else None
