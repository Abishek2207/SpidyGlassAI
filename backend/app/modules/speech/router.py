from fastapi import APIRouter, Depends
from app.core.security import get_current_user_id
from app.modules.speech.schema import SpeechTranscribeRequest, SpeechTranscribeResponse
from app.modules.speech.service import SpeechService

router = APIRouter(prefix="/speech", tags=["Speech Service"])
_service = SpeechService()


@router.post("/transcribe", response_model=SpeechTranscribeResponse)
async def transcribe_audio(
    req: SpeechTranscribeRequest,
    _: int = Depends(get_current_user_id),
):
    """Transcribe audio to text using Sarvam AI STT."""
    return await _service.transcribe(req)
