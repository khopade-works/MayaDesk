"""Application settings loaded from the environment / .env file.

All configuration for MayaDesk flows through :class:`Settings`. Values are read
once and cached via :func:`get_settings` so the rest of the codebase can depend
on a single, validated configuration object.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    """Typed, validated application configuration.

    Reads from environment variables and an optional ``.env`` file. Unknown
    environment variables are ignored so unrelated tooling config does not
    cause a fail-fast error.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Core runtime ---------------------------------------------------
    database_url: str = Field(
        default="sqlite+aiosqlite:///./maya.db",
        alias="DATABASE_URL",
    )
    env: str = Field(default="development", alias="ENV")
    log_level: str = Field(default="info", alias="LOG_LEVEL")
    # ``NoDecode`` stops pydantic-settings from JSON-parsing the raw env value;
    # the validator below splits a plain comma-separated string instead.
    cors_origins: Annotated[list[str], NoDecode] = Field(
        default_factory=list,
        alias="CORS_ORIGINS",
    )

    # --- LiveKit (voice transport, wired in Phase 3) --------------------
    livekit_url: str | None = Field(default=None, alias="LIVEKIT_URL")
    livekit_api_key: str | None = Field(default=None, alias="LIVEKIT_API_KEY")
    livekit_api_secret: str | None = Field(default=None, alias="LIVEKIT_API_SECRET")

    # --- Groq (LLM + STT, wired in Phase 3) -----------------------------
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    groq_llm_model: str = Field(
        default="llama-3.3-70b-versatile",
        alias="GROQ_LLM_MODEL",
    )
    groq_stt_model: str = Field(
        default="whisper-large-v3",
        alias="GROQ_STT_MODEL",
    )

    # --- Hardening (rate limiting) ---------------------------------------
    rate_limit_enabled: bool = Field(default=True, alias="RATE_LIMIT_ENABLED")
    rate_limit_default: str = Field(default="120/minute", alias="RATE_LIMIT_DEFAULT")
    rate_limit_token: str = Field(default="10/minute", alias="RATE_LIMIT_TOKEN")

    # --- Realtime events (agent -> API internal push) --------------------
    # Shared secret guarding the internal event endpoint. When unset (dev),
    # the endpoint accepts unauthenticated posts; set it in production.
    internal_event_token: str | None = Field(
        default=None, alias="INTERNAL_EVENT_TOKEN"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_cors_origins(cls, value: object) -> object:
        """Accept a comma-separated string and normalise it to a list."""
        if value is None or value == "":
            return []
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value

    @field_validator("env")
    @classmethod
    def _normalise_env(cls, value: str) -> str:
        return value.strip().lower()

    @field_validator("log_level")
    @classmethod
    def _normalise_log_level(cls, value: str) -> str:
        return value.strip().lower()

    @property
    def is_production(self) -> bool:
        """True when running in a production-like environment."""
        return self.env in {"production", "prod"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the process-wide, cached :class:`Settings` instance.

    Fails fast at first call if the environment is misconfigured.
    """
    return Settings()
