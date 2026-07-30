import time
import logging
import httpx
from app.core.config import settings
from app.core.exceptions import SarvamAPIException, ServiceUnavailableException
from app.modules.translation.schema import TranslationRequest, TranslationResponse

logger = logging.getLogger("spiderglass.translation")

SARVAM_TRANSLATE_URL = f"{settings.sarvam_base_url}/translate"


class TranslationService:
    """Calls Sarvam AI translation API."""

    async def translate(self, req: TranslationRequest) -> TranslationResponse:
        start = time.time()

        if not settings.sarvam_api_key or settings.sarvam_api_key == "your-sarvam-api-key-here":
            logger.info("Demo Mode: Returning mocked translation.")
            # Produce a realistic demo translation that reflects the input
            demo_translations = {
                "en-IN": req.input,
                "hi-IN": f"[DEMO PROVIDER] {req.input} (हिंदी अनुवाद उपलब्ध होगा जब Sarvam AI कॉन्फ़िगर हो)",
                "ta-IN": f"[DEMO PROVIDER] {req.input} (தமிழ் மொழிபெயர்ப்பு Sarvam AI உடன் கிடைக்கும்)",
                "te-IN": f"[DEMO PROVIDER] {req.input} (తెలుగు అనువాదం Sarvam AI తో అందుబాటులో ఉంటుంది)",
            }
            translated = demo_translations.get(
                req.target_language_code,
                f"[DEMO PROVIDER] Translation of: {req.input[:80]}..."
            )
            return TranslationResponse(
                translated_text=translated,
                source_language_code=req.source_language_code,
                target_language_code=req.target_language_code,
                processing_time_ms=int((time.time() - start) * 1000),
            )

        payload = {
            "input": req.input,
            "source_language_code": req.source_language_code,
            "target_language_code": req.target_language_code,
            "speaker_gender": req.speaker_gender,
            "mode": req.mode,
            "model": "mayura:v1",
            "enable_preprocessing": req.enable_preprocessing,
        }
        headers = {
            "Content-Type": "application/json",
            "api-subscription-key": settings.sarvam_api_key,
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                resp = await client.post(SARVAM_TRANSLATE_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise SarvamAPIException(f"HTTP {resp.status_code}: {resp.text}")

                result = resp.json()
                translated = result.get("translated_text", "")
                logger.info(f"Translation success: {req.source_language_code} → {req.target_language_code}")

                return TranslationResponse(
                    translated_text=translated,
                    source_language_code=req.source_language_code,
                    target_language_code=req.target_language_code,
                    processing_time_ms=int((time.time() - start) * 1000),
                )
            except httpx.TimeoutException:
                raise ServiceUnavailableException("Sarvam Translation")
            except SarvamAPIException:
                raise
            except Exception as e:
                logger.error(f"Translation error: {e}")
                raise SarvamAPIException(str(e))
