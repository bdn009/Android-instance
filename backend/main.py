import logging
from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database.database import init_db
from app.logging_config import setup_logging
from app.middleware import RateLimitMiddleware, RequestLoggingMiddleware

# Import routers
from app.api.auth import router as auth_router
from app.api.instances import router as instances_router
from app.api.apk import router as apk_router
from app.api.streaming import router as streaming_router

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("🚀 Starting Cloud Android Instance Manager")

    # Initialize database tables
    await init_db()
    logger.info("✅ Database initialized")

    # Initialize Redis connection
    try:
        app.state.redis = aioredis.from_url(
            settings.REDIS_URL, decode_responses=False
        )
        await app.state.redis.ping()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️  Redis not available: {e} — running without cache")
        app.state.redis = None

    yield

    # Shutdown
    if app.state.redis:
        await app.state.redis.close()
    logger.info("👋 Application shutdown complete")


# ──────────────────────────── App ────────────────────────────

app = FastAPI(
    title="Cloud Android Instance Manager",
    description="Manage server-hosted Android (Waydroid) instances via a web API",
    version="1.0.0",
    lifespan=lifespan,
)

# ──────────────────────────── CORS ────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────── Custom Middleware ────────────────────────────

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware)

# ──────────────────────────── Routers ────────────────────────────

app.include_router(auth_router)
app.include_router(instances_router)
app.include_router(apk_router)
app.include_router(streaming_router)


# ──────────────────────────── Health ────────────────────────────

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "healthy", "service": "cloudroid-api"}


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Cloud Android Instance Manager API",
        "docs": "/docs",
        "version": "1.0.0",
    }
