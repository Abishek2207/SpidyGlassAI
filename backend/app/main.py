"""
SpiderGlass AI – FastAPI Application Entry Point
Production-ready setup: CORS, lifespan, exception handlers, routers.
"""
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.core.redis_client import get_redis, close_redis
from app.core.logging import configure_logging
from app.core.exceptions import register_exception_handlers
from app.api.router import api_router
from app.modules.device.router import router as ws_router
from app.modules.agent.router import router as agent_router
from app.api.cron import router as cron_router

# Configure structured logging first
configure_logging()
logger = logging.getLogger("spiderglass")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} [{settings.app_env}]")

    # Initialise PostgreSQL tables
    await init_db()
    logger.info("PostgreSQL tables initialised.")

    # Warm up Redis connection
    try:
        await get_redis()
        logger.info("Redis connection established.")
    except Exception as e:
        logger.warning(f"Redis unavailable (continuing without it): {e}")

    yield

    # Shutdown
    await close_redis()
    logger.info(f"{settings.app_name} shut down cleanly.")


# ── Create FastAPI app ────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-ready AI assistive communication backend. "
        "Powered by Sarvam AI, MediaPipe, FastAPI, PostgreSQL, Redis."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ────────────────────────────────────────────────────────
register_exception_handlers(app)

# ── Mount REST API Gateway ────────────────────────────────────────────────────
app.include_router(api_router)

# ── Mount WebSocket Gateway ───────────────────────────────────────────────────
app.include_router(ws_router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "version": "2.0.0",
    }
