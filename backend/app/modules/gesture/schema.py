from pydantic import BaseModel
from typing import Optional, List


class Landmark(BaseModel):
    x: float
    y: float
    z: float


class GestureRecognizeRequest(BaseModel):
    landmarks: List[List[Landmark]]   # List of hands, each with 21 landmarks


class GestureResult(BaseModel):
    gesture: str
    confidence: float
    hand_index: int


class GestureRecognizeResponse(BaseModel):
    results: List[GestureResult]
    processing_time_ms: int
