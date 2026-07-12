from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.analytics.schema import EventIngestRequest, EventResponse, AnalyticsSummary
from app.modules.analytics.service import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["Analytics Service"])
_service = AnalyticsService()


@router.post("/events", response_model=EventResponse, status_code=201)
async def ingest_event(
    data: EventIngestRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Record a telemetry or usage event."""
    return await _service.record_event(db, data, user_id)


@router.get("/summary", response_model=AnalyticsSummary)
async def get_summary(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Get aggregated analytics summary for the current user."""
    return await _service.get_summary(db, user_id)
