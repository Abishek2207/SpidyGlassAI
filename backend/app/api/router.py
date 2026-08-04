"""
SpiderGlass AI – Central API Router (v1 gateway).
All REST routers are mounted here under /api/v1/.
"""
from fastapi import APIRouter
from app.modules.auth.router import router as auth_router
from app.modules.speech.router import router as speech_router
from app.modules.translation.router import router as translation_router
from app.modules.tts.router import router as tts_router
from app.modules.llm.router import router as llm_router
from app.modules.camera.router import router as camera_router
from app.modules.gesture.router import router as gesture_router
from app.modules.agent.router import router as agent_router
from app.modules.settings.router import router as settings_router
from app.modules.analytics.router import router as analytics_router
from app.modules.rag.router import router as rag_router
from app.modules.system.router import router as system_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth_router)
api_router.include_router(speech_router)
api_router.include_router(translation_router)
api_router.include_router(tts_router)
api_router.include_router(llm_router)
api_router.include_router(camera_router)
api_router.include_router(gesture_router)
api_router.include_router(agent_router)
api_router.include_router(settings_router)
api_router.include_router(analytics_router)
api_router.include_router(rag_router)
api_router.include_router(system_router)
