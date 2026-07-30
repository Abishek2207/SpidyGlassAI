from pydantic import BaseModel
from typing import List, Optional


class CameraFrameRequest(BaseModel):
    image_base64: str      # JPEG/PNG frame as base64


class DetectedHand(BaseModel):
    hand_index: int
    handedness: str        # "Left" | "Right"
    landmarks: List[dict]  # [{x, y, z}, ...]


class DetectedObject(BaseModel):
    label: str
    confidence: float
    bbox: List[float]      # [x_min, y_min, x_max, y_max]


class DetectedFace(BaseModel):
    confidence: float
    bbox: List[float]      # [x_min, y_min, x_max, y_max]


class CameraFrameResponse(BaseModel):
    hands_detected: int
    hands: List[DetectedHand]
    objects: List[DetectedObject] = []
    faces: List[DetectedFace] = []
    annotated_image_base64: Optional[str] = None
    processing_time_ms: int
