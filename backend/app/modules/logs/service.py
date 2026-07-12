"""
SpiderGlass AI – Logs Service.
Provides async helper functions to write telemetry and events to the database.
"""
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.logs.models import ConversationHistory, GestureLog, SpeechLog, TranslationLog, SystemLog

class LogsService:
    @staticmethod
    async def log_conversation(
        db: AsyncSession,
        user_id: int,
        session_id: str,
        input_text: Optional[str] = None,
        translated_input: Optional[str] = None,
        ai_response: Optional[str] = None,
        source_language: Optional[str] = None,
        target_language: Optional[str] = None,
        processing_time_ms: int = 0
    ) -> ConversationHistory:
        log = ConversationHistory(
            user_id=user_id,
            session_id=session_id,
            input_text=input_text,
            translated_input=translated_input,
            ai_response=ai_response,
            source_language=source_language,
            target_language=target_language,
            processing_time_ms=processing_time_ms
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_gesture(
        db: AsyncSession,
        user_id: int,
        gesture_name: str,
        confidence: float,
        processing_time_ms: int = 0
    ) -> GestureLog:
        log = GestureLog(
            user_id=user_id,
            gesture_name=gesture_name,
            confidence=confidence,
            processing_time_ms=processing_time_ms
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_speech(
        db: AsyncSession,
        user_id: int,
        audio_duration_ms: Optional[int],
        language: Optional[str],
        transcript: Optional[str],
        processing_time_ms: int = 0
    ) -> SpeechLog:
        log = SpeechLog(
            user_id=user_id,
            audio_duration_ms=audio_duration_ms,
            language=language,
            transcript=transcript,
            processing_time_ms=processing_time_ms
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_translation(
        db: AsyncSession,
        user_id: int,
        source_language: str,
        target_language: str,
        char_count: int,
        processing_time_ms: int = 0
    ) -> TranslationLog:
        log = TranslationLog(
            user_id=user_id,
            source_language=source_language,
            target_language=target_language,
            char_count=char_count,
            processing_time_ms=processing_time_ms
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def log_system_event(
        db: AsyncSession,
        level: str,
        module: str,
        message: str,
        details: Optional[Dict[str, Any]] = None
    ) -> SystemLog:
        log = SystemLog(
            level=level,
            module=module,
            message=message,
            details=details
        )
        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log
