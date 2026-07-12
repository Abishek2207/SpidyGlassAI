from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.tts.schema import TTSRequest, TTSResponse
from app.modules.tts.service import TTSService

router = APIRouter(prefix="/tts", tags=["Text-to-Speech Service"])
_service = TTSService()


@router.post("/synthesize", response_model=TTSResponse)
async def synthesize_speech(
    req: TTSRequest,
    _: int = Depends(get_current_user_id),
):
    """Convert text to speech audio using Sarvam AI bulbul model."""
    return await _service.synthesize(req)
