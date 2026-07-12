from pydantic import BaseModel
from typing import Optional


class TTSRequest(BaseModel):
    inputs: list[str]
    target_language_code: str = "hi-IN"
    speaker: str = "meera"          # Sarvam speaker name
    pitch: float = 0.0
    pace: float = 1.0
    loudness: float = 1.0
    speech_sample_rate: int = 22050
    enable_preprocessing: bool = True
    model: str = "bulbul:v1"


class TTSResponse(BaseModel):
    audios: list[str]               # Base64 encoded WAV audio chunks
    processing_time_ms: int
