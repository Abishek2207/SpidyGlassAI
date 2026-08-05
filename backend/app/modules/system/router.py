from fastapi import APIRouter, Depends
import psutil
import httpx
import time
import os
import torch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.config import settings
from app.core.database import get_db
from app.core.redis_client import get_redis

router = APIRouter(tags=["System Info"])

@router.get("/system/status")
@router.get("/system")
async def get_system_status(db: AsyncSession = Depends(get_db)):
    start = time.time()
    
    # 1. Database Check
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    # 2. Redis Check
    try:
        r = await get_redis()
        await r.ping()
        redis_status = "connected"
    except Exception:
        redis_status = "disconnected"
        
    # 3. Sarvam Check
    sarvam_status = "connected" if (settings.sarvam_api_key and settings.sarvam_api_key != "your-sarvam-api-key-here") else "missing"
    
    # 4. Model Check
    model_status = "loaded" if os.path.exists("models/sign_language_model.pt") else "missing"
    
    latency_ms = int((time.time() - start) * 1000)
    
    return {
        "database": db_status,
        "redis": redis_status,
        "sarvam": sarvam_status,
        "model": model_status,
        "websocket": "running",
        "device": "GPU" if torch.cuda.is_available() else "CPU",
        "latency": f"{latency_ms}ms",
        "cpu": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent,
        "mode": "offline" if settings.offline_mode else "online"
    }

@router.get("/ollama")
async def get_ollama_status():
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            if resp.status_code == 200:
                models = [m["name"] for m in resp.json().get("models", [])]
                return {"status": "online", "models": models}
    except Exception:
        pass
    return {"status": "offline", "models": []}

