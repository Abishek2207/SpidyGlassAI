import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.settings.models import UserSettings
from app.modules.settings.schema import SettingsUpdateRequest

logger = logging.getLogger("spiderglass.settings")


class SettingsService:

    async def get_or_create(self, db: AsyncSession, user_id: int) -> UserSettings:
        result = await db.execute(select(UserSettings).where(UserSettings.user_id == user_id))
        settings = result.scalar_one_or_none()
        if not settings:
            settings = UserSettings(user_id=user_id)
            db.add(settings)
            await db.flush()
            await db.refresh(settings)
            logger.info(f"Created default settings for user {user_id}")
        return settings

    async def update(self, db: AsyncSession, user_id: int, data: SettingsUpdateRequest) -> UserSettings:
        settings = await self.get_or_create(db, user_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(settings, field, value)
        await db.flush()
        await db.refresh(settings)
        logger.info(f"Updated settings for user {user_id}")
        return settings
