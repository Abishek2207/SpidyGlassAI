import time
import logging
import httpx
from app.core.config import settings
from app.core.exceptions import SarvamAPIException, ServiceUnavailableException
from app.modules.llm.schema import LLMRequest, LLMResponse

logger = logging.getLogger("spiderglass.llm")

# Sarvam uses an OpenAI-compatible chat completions endpoint
SARVAM_LLM_URL = f"{settings.sarvam_base_url}/v1/chat/completions"
SARVAM_LLM_MODEL = "sarvam-m"


class LLMService:
    """Calls Sarvam AI LLM (sarvam-m) via OpenAI-compatible API."""

    async def chat(self, req: LLMRequest) -> LLMResponse:
        start = time.time()

        if not settings.sarvam_api_key or settings.sarvam_api_key == "your-sarvam-api-key-here":
            logger.error("Sarvam API key is missing. Refusing to run in demo mode.")
            raise SarvamAPIException("SARVAM_API_KEY is not configured.")

        messages = [{"role": "system", "content": req.system_prompt}]
        messages += [{"role": m.role, "content": m.content} for m in req.messages]

        payload = {
            "model": SARVAM_LLM_MODEL,
            "messages": messages,
            "max_tokens": req.max_tokens,
            "temperature": req.temperature,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.sarvam_api_key}",
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                resp = await client.post(SARVAM_LLM_URL, json=payload, headers=headers)
                if resp.status_code != 200:
                    raise SarvamAPIException(f"HTTP {resp.status_code}: {resp.text}")

                result = resp.json()
                choice = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                logger.info("LLM response received successfully.")

                return LLMResponse(
                    reply=choice,
                    model=result.get("model", SARVAM_LLM_MODEL),
                    prompt_tokens=usage.get("prompt_tokens"),
                    completion_tokens=usage.get("completion_tokens"),
                    processing_time_ms=int((time.time() - start) * 1000),
                )
            except httpx.TimeoutException:
                raise ServiceUnavailableException("Sarvam LLM")
            except SarvamAPIException:
                raise
            except Exception as e:
                logger.error(f"LLM error: {e}")
                raise SarvamAPIException(str(e))
