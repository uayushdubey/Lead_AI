"""Application configuration via Pydantic Settings.

All values are read from environment variables (or a .env file).
Call `get_settings()` anywhere in the application — it returns a cached
singleton so the .env file is parsed exactly once per process.
"""

from functools import lru_cache

from pydantic import PostgresDsn, RedisDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Typed, validated application settings.

    Pydantic-settings reads values from:
      1. Environment variables (highest priority)
      2. .env file (fallback)
      3. Field defaults (lowest priority)

    Validation runs at instantiation time — bad values raise at startup,
    not buried inside a request handler at runtime.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,   # APP_NAME and app_name both work
        extra="ignore",         # Unknown env vars are silently ignored
    )

    # ── Application ───────────────────────────────────────────────────────────
    app_name: str = "LeadForge AI"
    app_env: str = "development"        # "development" | "staging" | "production"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # ── Security ──────────────────────────────────────────────────────────────
    secret_key: str                     # Required — no default; must be in .env
    access_token_expire_minutes: int = 30

    # ── Database ──────────────────────────────────────────────────────────────
    database_url: PostgresDsn           # Validated as a proper PostgreSQL DSN

    # ── Redis ─────────────────────────────────────────────────────────────────
    redis_url: RedisDsn                 # Validated as a proper Redis DSN

    # ── Derived helpers ───────────────────────────────────────────────────────
    @property
    def is_development(self) -> bool:
        """True when running in a local dev environment."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """True when running in a production environment."""
        return self.app_env == "production"


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Return the application settings singleton.

    The result is cached after the first call — `.env` is read only once.
    In tests, call `get_settings.cache_clear()` before overriding env vars.
    """
    return AppSettings()  # type: ignore[call-arg]
