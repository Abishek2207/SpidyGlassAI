from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_current_user_id
from app.core.database import get_db
from app.modules.speech.schema import SpeechTranscribeRequest, SpeechTranscribeResponse
from app.modules.speech.service import SpeechService
from app.modules.logs.service import LogsService
import base64

router = APIRouter(prefix="/speech", tags=["Speech Service"])
_service = SpeechService()

@router.post("/transcribe", response_model=SpeechTranscribeResponse)
async def transcribe_audio(
    req: SpeechTranscribeRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    """Transcribe audio to text using Sarvam AI STT."""
    resp = await _service.transcribe(req)
    
    # Calculate rough duration from base64 size if needed, or leave None
    audio_duration_ms = int(len(req.audio_base64) * 0.75 / (16000 * 2)) * 1000  # assuming 16kHz 16-bit PCM

    await LogsService.log_speech(
        db=db,
        user_id=user_id,
        audio_duration_ms=audio_duration_ms,
        language=resp.language_code,
        transcript=resp.transcript,
        processing_time_ms=resp.processing_time_ms
    )
    
    return resp
