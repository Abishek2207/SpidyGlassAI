from typing import Optional
from pydantic import BaseModel


class SettingsResponse(BaseModel):
    user_id: int
    preferred_language: str
    tts_speaker: str
    tts_speed: str
    gesture_sensitivity: str
    extra: dict

    model_config = {"from_attributes": True}


class SettingsUpdateRequest(BaseModel):
    preferred_language: Optional[str] = None
    tts_speaker: Optional[str] = None
    tts_speed: Optional[str] = None
    gesture_sensitivity: Optional[str] = None
    extra: Optional[dict] = None
