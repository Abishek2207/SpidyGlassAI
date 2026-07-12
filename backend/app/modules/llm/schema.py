from pydantic import BaseModel
from typing import Optional


class LLMMessage(BaseModel):
    role: str        # "user" | "assistant" | "system"
    content: str


class LLMRequest(BaseModel):
    messages: list[LLMMessage]
    max_tokens: int = 512
    temperature: float = 0.7
    system_prompt: str = (
        "You are VisionVoice AI, an assistive communication assistant for "
        "speech-impaired and hearing-impaired users. Respond helpfully, "
        "concisely, and empathetically in the same language as the user."
    )


class LLMResponse(BaseModel):
    reply: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    processing_time_ms: int
