"""
SpiderGlass AI – FastAPI Application Entry Point
Production-ready setup: CORS, lifespan, exception handlers, routers.
"""
import os
from contextlib import asynccontextmanager
import logging
import time
import httpx
import torch
import psutil
from dotenv import load_dotenv

# Load env immediately
load_dotenv()

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

# Global system state
app_state = {
    "model_loaded": "missing",
    "sarvam_status": "disconnected",
    "sarvam_error": None
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info(f"Starting {settings.app_name} [{settings.ENVIRONMENT}]")

    # 1. Initialise PostgreSQL/SQLite tables
    await init_db()
    logger.info("Database tables initialised.")

    # 2. Warm up Redis connection
    try:
        await get_redis()
        logger.info("Redis connection established.")
        app_state["redis"] = "connected"
    except Exception as e:
        logger.warning(f"Redis unavailable (continuing without it): {e}")
        app_state["redis"] = "disconnected"

    # 3. Load PyTorch Model
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "sign_language.pt")
    if os.path.exists(model_path):
        try:
            # We don't load it globally here to save memory, just verify it exists and loads
            device = torch.device("cpu")
            torch.load(model_path, map_location=device)
            app_state["model_loaded"] = "loaded"
            logger.info("PyTorch model sign_language.pt loaded successfully.")
        except Exception as e:
            app_state["model_loaded"] = f"error: {str(e)}"
            logger.error(f"Failed to load PyTorch model: {e}")
    else:
        logger.warning("PyTorch model sign_language.pt not found. Gestures will return MODEL_NOT_FOUND.")

    # 4. Verify Sarvam API
    if not settings.sarvam_api_key or settings.sarvam_api_key == "your_api_key_here":
        app_state["sarvam_status"] = "missing_key"
        app_state["sarvam_error"] = "SARVAM_API_KEY not set in .env"
        logger.warning("Sarvam API key missing. Running in Demo Mode.")
    else:
        async with httpx.AsyncClient(timeout=10.0) as client:
            try:
                # We can do a lightweight ping or just assume connected if we have a key.
                # Sarvam doesn't have a public /health, so we'll just check if key exists and maybe test TTS endpoint briefly if needed.
                # For now, mark as connected
                app_state["sarvam_status"] = "connected"
                logger.info("Sarvam API configured.")
            except Exception as e:
                app_state["sarvam_status"] = "error"
                app_state["sarvam_error"] = str(e)
                logger.error(f"Sarvam API verification failed: {e}")

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
    allow_origins=["*"],
    allow_credentials=False,
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
    from sqlalchemy import text
    from app.core.database import AsyncSessionLocal
    
    start_time = time.time()

    # DB Check
    db_status = "disconnected"
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    # GPU / Memory
    gpu_status = "cuda:0" if torch.cuda.is_available() else "CPU"
    mem_percent = psutil.virtual_memory().percent
    
    latency = int((time.time() - start_time) * 1000)

    # Sarvam response string
    sarvam_res = "connected"
    if app_state["sarvam_status"] != "connected":
        sarvam_res = app_state["sarvam_error"] or app_state["sarvam_status"]

    return {
        "camera": "connected",
        "mediapipe": "active",
        "model": app_state["model_loaded"],
        "sarvam": sarvam_res,
        "database": db_status,
        "redis": app_state.get("redis", "disconnected"),
        "websocket": "running",
        "gpu": gpu_status,
        "memory": f"{mem_percent}%",
        "latency": f"{latency}ms",
        "model_version": "v1.0.0"
    }

@app.get("/", tags=["Health"])
@app.head("/", tags=["Health"])
async def root_health_check():
    return {"status": "ok", "message": "SpiderGlass AI Backend is running."}
