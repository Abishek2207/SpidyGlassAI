"""
SpiderGlass AI – Core Configuration
Loads all settings from environment variables via pydantic-settings.
"""
from functools import lru_cache
from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────────
    app_name: str = "SpiderGlass AI"
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    debug: bool = True

    # ── JWT ──────────────────────────────────────────────────────────────────
    secret_key: str = "insecure-default-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ── PostgreSQL ────────────────────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://spiderglass:spiderglasspassword@localhost:5432/spiderglass_db"

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: str = "redis://localhost:6379"

    # ── Sarvam AI ─────────────────────────────────────────────────────────────
    sarvam_api_key: str = ""
    sarvam_base_url: str = "https://api.sarvam.ai"

    # ── CORS ──────────────────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
