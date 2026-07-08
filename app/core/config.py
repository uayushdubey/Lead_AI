"""Application configuration via Pydantic Settings."""

from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All settings are read from environment variables (or .env file)."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str

    # Database
    database_url: PostgresDsn

    # Redis
    redis_url: RedisDsn

    # Celery
    celery_broker_url: str
    celery_result_backend: str


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached singleton of the application settings."""
    return Settings()  # type: ignore[call-arg]
