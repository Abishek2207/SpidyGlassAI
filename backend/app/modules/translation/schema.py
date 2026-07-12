from pydantic import BaseModel
from typing import Optional


class TranslationRequest(BaseModel):
    input: str
    source_language_code: str = "en-IN"
    target_language_code: str = "hi-IN"
    speaker_gender: str = "Male"
    mode: str = "formal"
    enable_preprocessing: bool = True


class TranslationResponse(BaseModel):
    translated_text: str
    source_language_code: str
    target_language_code: str
    processing_time_ms: int
