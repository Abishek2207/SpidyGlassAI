"""
SpiderGlass AI – Async database engine and session factory.
Local dev: SQLite (no Docker needed). Production: PostgreSQL via docker-compose.
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase


def _make_engine():
    """Build the engine lazily so it picks up the .env DATABASE_URL correctly."""
    # Import here to ensure .env is already loaded
    from app.core.config import settings
    url = settings.database_url

    # Fallback to SQLite if postgres not set or clearly a template value
    if not url or "postgresql" in url:
        # Check if we actually want sqlite for local dev
        import os
        if os.environ.get("USE_SQLITE", "true").lower() == "true" and "localhost" in url:
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
