"""
SpiderGlass AI – Alembic migration environment.
Supports both offline (SQL dump) and online (live DB) modes.
Uses synchronous psycopg2 engine for Alembic compatibility.
"""
import os
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# ── Import ALL models so Alembic can detect schema ───────────────────────────
from app.core.database import Base  # noqa: F401 – registers Base
from app.modules.auth.models import User  # noqa: F401
from app.modules.settings.models import UserSettings  # noqa: F401
from app.modules.analytics.models import AnalyticsEvent  # noqa: F401
from app.modules.logs.models import (  # noqa: F401
    ConversationHistory, GestureLog, SpeechLog, TranslationLog, SystemLog
)

# ── Build a SYNCHRONOUS URL for Alembic (it doesn't support asyncpg) ─────────
def _get_sync_url() -> str:
    raw = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://spiderglass:spiderglasspassword@localhost:5432/spiderglass_db"
    )
    # Replace async driver with sync psycopg2
    sync = raw.replace("postgresql+asyncpg", "postgresql+psycopg2")
    # Fall back to SQLite sync if still pointing to localhost without a real PG setup
    if "localhost" in sync or "127.0.0.1" in sync:
        try:
            import psycopg2  # noqa: F401
        except ImportError:
            sync = "sqlite:///./spiderglass_dev.db"
    return sync


config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

config.set_main_option("sqlalchemy.url", _get_sync_url())
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without a live DB connection (generates SQL)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
