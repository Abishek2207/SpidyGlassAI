import logging
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.modules.analytics.models import AnalyticsEvent
from app.modules.analytics.schema import EventIngestRequest, AnalyticsSummary

logger = logging.getLogger("spiderglass.analytics")


class AnalyticsService:

    async def record_event(
        self,
        db: AsyncSession,
        data: EventIngestRequest,
        user_id: Optional[int] = None,
    ) -> AnalyticsEvent:
        event = AnalyticsEvent(
            user_id=user_id,
            event_type=data.event_type,
            service=data.service,
            payload=data.payload,
            processing_time_ms=data.processing_time_ms,
        )
        db.add(event)
        await db.flush()
        logger.debug(f"Event recorded: {data.event_type} / {data.service}")
        return event

    async def get_summary(self, db: AsyncSession, user_id: Optional[int] = None) -> AnalyticsSummary:
        query = select(AnalyticsEvent)
        if user_id:
            query = query.where(AnalyticsEvent.user_id == user_id)

        result = await db.execute(query)
        events = result.scalars().all()

        if not events:
            return AnalyticsSummary(
                total_events=0,
                events_by_service={},
                events_by_type={},
                avg_processing_time_ms=None,
            )

        by_service: dict[str, int] = {}
        by_type: dict[str, int] = {}
        total_time = 0.0
        timed_count = 0

        for e in events:
            by_service[e.service] = by_service.get(e.service, 0) + 1
            by_type[e.event_type] = by_type.get(e.event_type, 0) + 1
            if e.processing_time_ms is not None:
                total_time += e.processing_time_ms
                timed_count += 1

        return AnalyticsSummary(
            total_events=len(events),
            events_by_service=by_service,
            events_by_type=by_type,
            avg_processing_time_ms=round(total_time / timed_count, 2) if timed_count else None,
        )
