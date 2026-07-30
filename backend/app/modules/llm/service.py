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
            logger.info("Demo Mode: Returning contextual LLM response.")
            last_msg = req.messages[-1].content.strip() if req.messages else ""

            # Route to context-aware demo responses based on input keywords
            last_lower = last_msg.lower()
            if any(w in last_lower for w in ["hello", "hi", "namaste", "hey"]):
                reply = "[DEMO RESPONSE] Namaste! I am SpiderGlass AI — your intelligent assistive communication assistant. How can I help you today?"
            elif any(w in last_lower for w in ["sign", "gesture", "hand", "ily", "peace", "thumbs"]):
                reply = f"[DEMO RESPONSE] I recognised your sign gesture: '{last_msg[:60]}'. In ISL (Indian Sign Language), this communicates a clear intent. Would you like me to translate it or continue the conversation?"
            elif any(w in last_lower for w in ["translate", "hindi", "tamil", "language"]):
                reply = "[DEMO RESPONSE] Translation is powered by Sarvam AI's multilingual engine. Once configured with an API key, it supports Hindi, Tamil, Telugu, Kannada, Bengali, and 9 other Indian languages in real time."
            elif any(w in last_lower for w in ["demo", "investor", "presentation", "show"]):
                reply = "[DEMO RESPONSE] This is SpiderGlass AI — a real-time assistive communication platform combining Computer Vision, Sign Language Recognition, Speech-to-Text, AI responses, and Text-to-Speech into a seamless pipeline for the visually and hearing impaired."
            elif any(w in last_lower for w in ["camera", "video", "vision", "webcam"]):
                reply = "[DEMO RESPONSE] The Vision Agent is active. MediaPipe Hands extracts 21 landmarks per hand at ~18 FPS. YOLO v8 handles object detection every 5 frames to conserve CPU. All inference runs locally on your laptop."
            else:
                # Generic context-echo response
                preview = last_msg[:60] + ("..." if len(last_msg) > 60 else "")
                reply = f"[DEMO RESPONSE] Understood: '{preview}'. The multi-agent pipeline processed your input through Speech → Translation → LLM → TTS agents in under 200ms. Sarvam AI integration is ready — add your API key to enable live responses."

            return LLMResponse(
                reply=reply,
                model=SARVAM_LLM_MODEL,
                processing_time_ms=int((time.time() - start) * 1000),
            )

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
