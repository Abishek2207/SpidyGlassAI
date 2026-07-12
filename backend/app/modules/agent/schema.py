from pydantic import BaseModel
from typing import Optional, List


class AgentInput(BaseModel):
    """A unified input to the Agent Orchestrator."""
    text: Optional[str] = None
    audio_base64: Optional[str] = None
    image_base64: Optional[str] = None
    source_language: str = "en-IN"
    target_language: str = "hi-IN"
    session_id: Optional[str] = None


class AgentOutput(BaseModel):
    """The full AI pipeline output."""
    transcript: Optional[str] = None          # From STT
    translated_text: Optional[str] = None     # From Translation
    ai_reply: Optional[str] = None            # From LLM
    tts_audio_base64: Optional[str] = None    # From TTS
    gesture_detected: Optional[str] = None    # From Gesture
    pipeline_stages: List[str] = []           # Completed pipeline stages
    total_processing_time_ms: int = 0
    error: Optional[str] = None
