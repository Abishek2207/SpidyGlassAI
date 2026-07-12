from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, func
from app.core.database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)  # e.g. "gesture_detected"
    service = Column(String(50), nullable=False)                  # e.g. "gesture", "speech"
    payload = Column(JSON, nullable=True)
    processing_time_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
