"""
SpiderGlass AI – Async database engine and session factory.
Local dev: SQLite (no Docker needed). Production: PostgreSQL via docker-compose.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


def _make_engine():
    """Build the engine lazily so it picks up the .env DATABASE_URL correctly."""
    import os
    from app.core.config import settings

    url = settings.database_url
    environment = settings.ENVIRONMENT

    # In production (Render), if the user hasn't supplied a real PostgreSQL DATABASE_URL,
    # it will default to localhost. We must fallback to SQLite so the app doesn't crash.
    if "localhost" in url or "127.0.0.1" in url:
        url = "sqlite+aiosqlite:///./spiderglass_dev.db"

    connect_args = {"check_same_thread": False} if "sqlite" in url else {}
    return create_async_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )


engine = _make_engine()

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency: yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db() -> None:
    """Create all tables on application startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
