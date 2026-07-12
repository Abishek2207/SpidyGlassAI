from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.gesture.schema import GestureRecognizeRequest, GestureRecognizeResponse
from app.modules.gesture.service import GestureService

router = APIRouter(prefix="/gesture", tags=["Gesture Service"])
_service = GestureService()


@router.post("/recognize", response_model=GestureRecognizeResponse)
async def recognize_gesture(
    req: GestureRecognizeRequest,
    _: int = Depends(get_current_user_id),
):
    """Classify ISL hand gestures from MediaPipe landmarks."""
    return await _service.recognize(req)
