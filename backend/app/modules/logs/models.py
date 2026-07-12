"""
SpiderGlass AI – Enterprise Logging Models.
Tracks Conversation History, Gestures, Speech, Translation, and System Logs.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, JSON, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.modules.auth.models import User


class ConversationHistory(Base):
    """Stores full conversational turn data (STT -> Translation -> LLM -> TTS)."""
    __tablename__ = "conversation_history"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id = Column(String(50), index=True, nullable=False)
    
    input_text = Column(Text, nullable=True)         # From Speech or Keyboard
    translated_input = Column(Text, nullable=True)   # If source != target lang
    ai_response = Column(Text, nullable=True)        # LLM output
    
    source_language = Column(String(20), nullable=True)
    target_language = Column(String(20), nullable=True)
    
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User")


class GestureLog(Base):
    """Tracks detected gestures over time for analytics and tuning."""
    __tablename__ = "gesture_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    gesture_name = Column(String(50), index=True, nullable=False)
    confidence = Column(Float, nullable=False)
    processing_time_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SpeechLog(Base):
    """Tracks STT operations and metrics."""
    __tablename__ = "speech_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    audio_duration_ms = Column(Integer, nullable=True)
    language = Column(String(20), nullable=True)
    transcript = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class TranslationLog(Base):
    """Tracks Translation operations."""
    __tablename__ = "translation_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    source_language = Column(String(20), nullable=False)
    target_language = Column(String(20), nullable=False)
    char_count = Column(Integer, nullable=False)
    processing_time_ms = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)


class SystemLog(Base):
    """Captures general system events, errors, and agent state transitions."""
    __tablename__ = "system_logs"
    id = Column(Integer, primary_key=True, index=True)
    
    level = Column(String(20), index=True, nullable=False) # INFO, WARNING, ERROR
    module = Column(String(50), index=True, nullable=False)
    message = Column(Text, nullable=False)
    details = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
