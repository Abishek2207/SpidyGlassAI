from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import get_current_user_id
from app.modules.settings.schema import SettingsResponse, SettingsUpdateRequest
from app.modules.settings.service import SettingsService

router = APIRouter(prefix="/settings", tags=["Settings Service"])
_service = SettingsService()


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve the current user's preferences."""
    return await _service.get_or_create(db, user_id)


@router.patch("/", response_model=SettingsResponse)
async def update_settings(
    data: SettingsUpdateRequest,
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db),
):
    """Update user preferences (partial update supported)."""
    return await _service.update(db, user_id, data)
