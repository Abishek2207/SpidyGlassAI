import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.modules.auth.models import User
from app.modules.auth.schema import UserRegisterRequest
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import NotFoundException, UnauthorizedException, ValidationException
from app.core.config import settings

logger = logging.getLogger("spiderglass.auth")


class AuthService:

    async def register(self, db: AsyncSession, data: UserRegisterRequest) -> User:
        # Check if email already exists
        result = await db.execute(select(User).where(User.email == data.email))
        if result.scalar_one_or_none():
            raise ValidationException("Email is already registered.")

        # Check if username already taken
        result = await db.execute(select(User).where(User.username == data.username))
        if result.scalar_one_or_none():
            raise ValidationException("Username is already taken.")

        user = User(
            email=data.email,
            username=data.username,
            hashed_password=hash_password(data.password),
        )
        db.add(user)
        await db.flush()
        await db.refresh(user)
        logger.info(f"New user registered: {user.email}")
        return user

    async def login(self, db: AsyncSession, email: str, password: str) -> dict:
        result = await db.execute(select(User).where(User.email == email))
        user: User | None = result.scalar_one_or_none()

        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException("Invalid email or password.")

        if not user.is_active:
            raise UnauthorizedException("Account is disabled.")

        token = create_access_token(data={"sub": str(user.id)})
        logger.info(f"User logged in: {user.email}")
        return {
            "access_token": token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,
        }

    async def get_user_by_id(self, db: AsyncSession, user_id: int) -> User:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise NotFoundException("User", user_id)
        return user
