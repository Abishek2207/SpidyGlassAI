from pydantic import BaseModel
from typing import Optional


class SpeechTranscribeRequest(BaseModel):
    audio_base64: str                 # Base64-encoded audio bytes
    language_code: str = "hi-IN"     # BCP-47 language code
    model: str = "saarika:v2"        # Sarvam STT model


class SpeechTranscribeResponse(BaseModel):
    transcript: str
    language_code: str
    confidence: Optional[float] = None
    processing_time_ms: int
