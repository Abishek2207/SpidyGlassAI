from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user_id
from app.core.database import get_db
from app.modules.gesture.schema import GestureRecognizeRequest, GestureRecognizeResponse
from app.modules.gesture.service import GestureService
from app.modules.logs.service import LogsService

router = APIRouter(prefix="/gesture", tags=["Gesture Service"])
_service = GestureService()

@router.post("/recognize", response_model=GestureRecognizeResponse)
async def recognize_gesture(
    req: GestureRecognizeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Classify ISL hand gestures from MediaPipe landmarks."""
    resp, sentence = await _service.recognize(req)
    
    # Fire off log asynchronously to not block return if needed, but here we just await it 
    if resp.results:
        top_result = resp.results[0]
        await LogsService.log_gesture(
            db=db,
            user_id=user_id,
            gesture_name=top_result.gesture,
            confidence=top_result.confidence,
            processing_time_ms=top_result.latency
        )
        
    return resp
