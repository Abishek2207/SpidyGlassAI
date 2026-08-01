import base64
import time
import logging
import httpx
from app.core.config import settings
from app.core.exceptions import SarvamAPIException, ServiceUnavailableException
from app.modules.speech.schema import SpeechTranscribeRequest, SpeechTranscribeResponse

logger = logging.getLogger("spiderglass.speech")

SARVAM_STT_URL = f"{settings.sarvam_base_url}/speech-to-text"


class SpeechService:
    """
    Calls Sarvam AI speech-to-text API.
    Falls back to a mock transcript if no API key is configured.
    """

    async def transcribe(self, req: SpeechTranscribeRequest) -> SpeechTranscribeResponse:
        start = time.time()

        if not settings.sarvam_api_key or settings.sarvam_api_key == "your-sarvam-api-key-here":
            logger.error("Sarvam API key is missing. Refusing to run in demo mode.")
            raise SarvamAPIException("SARVAM_API_KEY is not configured.")

        try:
            audio_bytes = base64.b64decode(req.audio_base64)
        except Exception:
            raise SarvamAPIException("Invalid base64 audio data.")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                files = {"file": ("audio.wav", audio_bytes, "audio/wav")}
                data = {
                    "model": req.model,
                    "language_code": req.language_code,
                    "with_timestamps": "false",
                    "with_disfluencies": "false",
                }
                headers = {"api-subscription-key": settings.sarvam_api_key}

                resp = await client.post(SARVAM_STT_URL, files=files, data=data, headers=headers)

                if resp.status_code != 200:
                    raise SarvamAPIException(f"HTTP {resp.status_code}: {resp.text}")

                result = resp.json()
                transcript = result.get("transcript", "")
                logger.info(f"STT success: {len(transcript)} chars")

                return SpeechTranscribeResponse(
                    transcript=transcript,
                    language_code=req.language_code,
                    confidence=result.get("confidence"),
                    processing_time_ms=int((time.time() - start) * 1000),
                )

            except httpx.TimeoutException:
                raise ServiceUnavailableException("Sarvam STT")
            except SarvamAPIException:
                raise
            except Exception as e:
                logger.error(f"STT error: {e}")
                raise SarvamAPIException(str(e))
