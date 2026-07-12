from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.camera.schema import CameraFrameRequest, CameraFrameResponse
from app.modules.camera.service import CameraService

router = APIRouter(prefix="/camera", tags=["Camera Service"])
_service = CameraService()


@router.post("/process-frame", response_model=CameraFrameResponse)
async def process_frame(
    req: CameraFrameRequest,
    _: int = Depends(get_current_user_id),
):
    """Process a video frame for hand detection using MediaPipe."""
    return await _service.process_frame(req)
