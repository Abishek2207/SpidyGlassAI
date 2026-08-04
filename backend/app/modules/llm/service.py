import time
import logging
import httpx
from app.core.config import settings
from app.core.exceptions import SarvamAPIException, ServiceUnavailableException
from app.modules.llm.schema import LLMRequest, LLMResponse

logger = logging.getLogger("spiderglass.llm")

SARVAM_LLM_URL = f"{settings.sarvam_base_url}/v1/chat/completions"
SARVAM_LLM_MODEL = "sarvam-m"
PREFERRED_OFFLINE_MODELS = ["qwen2.5:7b", "llama3.1:8b", "mistral:7b"]

class LLMService:
    """Calls Sarvam AI LLM, or falls back to Ollama offline."""

    async def get_offline_model(self) -> str:
        """Fetch available models from Ollama."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.get(f"{settings.ollama_base_url}/api/tags")
                if resp.status_code == 200:
                    models = [m["name"] for m in resp.json().get("models", [])]
                    for pref in PREFERRED_OFFLINE_MODELS:
                        for m in models:
                            if pref in m:
                                return m
                    if models:
                        return models[0] # Return any model if preferences aren't met
        except Exception:
            pass
        return ""

    async def _chat_offline(self, req: LLMRequest, start_time: float) -> LLMResponse:
        model = await self.get_offline_model()
        if not model:
            raise ServiceUnavailableException("Offline Model Not Installed (Ollama)")

        logger.info(f"Using offline model: {model}")
        
        messages = [{"role": "system", "content": req.system_prompt}]
        messages += [{"role": m.role, "content": m.content} for m in req.messages]

        payload = {
            "model": model,
            "messages": messages,
            "stream": False
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                resp = await client.post(f"{settings.ollama_base_url}/api/chat", json=payload)
                if resp.status_code != 200:
                    raise ServiceUnavailableException(f"Ollama Error: {resp.text}")
                
                result = resp.json()
                choice = result.get("message", {}).get("content", "")
                
                return LLMResponse(
                    reply=choice,
                    model=model,
                    prompt_tokens=result.get("prompt_eval_count"),
                    completion_tokens=result.get("eval_count"),
                    processing_time_ms=int((time.time() - start_time) * 1000),
                )
        except Exception as e:
            raise ServiceUnavailableException(f"Ollama Error: {str(e)}")

    async def chat(self, req: LLMRequest) -> LLMResponse:
        start = time.time()

        if settings.offline_mode or not settings.sarvam_api_key or settings.sarvam_api_key == "your-sarvam-api-key-here":
            logger.info("Operating in Offline Mode.")
            return await self._chat_offline(req, start)

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
                    logger.warning("Sarvam API failed. Falling back to offline mode.")
                    return await self._chat_offline(req, start)

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
                logger.warning("Sarvam LLM Timeout. Falling back to offline mode.")
                return await self._chat_offline(req, start)
            except Exception as e:
                logger.error(f"LLM error: {e}. Falling back to offline.")
                return await self._chat_offline(req, start)
