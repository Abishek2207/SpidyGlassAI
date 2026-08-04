from fastapi import APIRouter
import psutil
import httpx
from app.core.config import settings

router = APIRouter(tags=["System Info"])

@router.get("/system")
def get_system_stats():
    return {
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
