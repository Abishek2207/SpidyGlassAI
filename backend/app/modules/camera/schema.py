from pydantic import BaseModel
from typing import List, Optional


class CameraFrameRequest(BaseModel):
    image_base64: str      # JPEG/PNG frame as base64


class DetectedHand(BaseModel):
    hand_index: int
    handedness: str        # "Left" | "Right"
    landmarks: List[dict]  # [{x, y, z}, ...]


class CameraFrameResponse(BaseModel):
    hands_detected: int
    hands: List[DetectedHand]
    annotated_image_base64: Optional[str] = None
    processing_time_ms: int
