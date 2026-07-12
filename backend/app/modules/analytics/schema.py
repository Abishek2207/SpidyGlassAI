from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel


class EventIngestRequest(BaseModel):
    event_type: str
    service: str
    payload: Optional[dict] = None
    processing_time_ms: Optional[float] = None


class EventResponse(BaseModel):
    id: int
    user_id: Optional[int]
    event_type: str
    service: str
    payload: Optional[dict]
    processing_time_ms: Optional[float]
    created_at: datetime

    model_config = {"from_attributes": True}


class AnalyticsSummary(BaseModel):
    total_events: int
    events_by_service: dict[str, int]
    events_by_type: dict[str, int]
    avg_processing_time_ms: Optional[float]
