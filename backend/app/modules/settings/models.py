from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from app.core.database import Base


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    preferred_language = Column(String(20), default="hi-IN")
    tts_speaker = Column(String(50), default="meera")
    tts_speed = Column(String(10), default="1.0")
    gesture_sensitivity = Column(String(10), default="0.6")
    extra = Column(JSON, default=dict)
