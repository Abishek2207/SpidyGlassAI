import time
import logging
import httpx
from app.core.config import settings
from app.core.exceptions import SarvamAPIException, ServiceUnavailableException
from app.modules.tts.schema import TTSRequest, TTSResponse

logger = logging.getLogger("spiderglass.tts")

SARVAM_TTS_URL = f"{settings.sarvam_base_url}/text-to-speech"


class TTSService:
    """Calls Sarvam AI text-to-speech (bulbul) API."""

    async def synthesize(self, req: TTSRequest) -> TTSResponse:
        start = time.time()

        if not settings.sarvam_api_key or settings.sarvam_api_key == "your-sarvam-api-key-here":
            raise SarvamAPIException("SARVAM_API_KEY is missing. Please configure your Sarvam API key to enable real Text-to-Speech.")

        payload = {
            "inputs": req.inputs,
            "target_language_code": req.target_language_code,
            "speaker": req.speaker,
            "pitch": req.pitch,
            "pace": req.pace,
            "loudness": req.loudness,
            "speech_sample_rate": req.speech_sample_rate,
            "enable_preprocessing": req.enable_preprocessing,
            "model": req.model,
        }
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": settings.sarvam_api_key,
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(SARVAM_TTS_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise SarvamAPIException(f"HTTP {resp.status_code}: {resp.text}")

                result = resp.json()
                audios = result.get("audios", [])
                logger.info(f"TTS success: {len(audios)} audio chunk(s) generated.")

                return TTSResponse(
                    audios=audios,
                    processing_time_ms=int((time.time() - start) * 1000),
                )
            except httpx.TimeoutException:
                raise ServiceUnavailableException("Sarvam TTS")
            except SarvamAPIException:
                raise
            except Exception as e:
                logger.error(f"TTS error: {e}")
                raise SarvamAPIException(str(e))
