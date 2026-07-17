"""Voice-pipeline tuning knobs for the Maya agent.

These control latency vs. responsiveness trade-offs and provider resilience.
They live in the agent (not the shared domain settings) because only the voice
worker consumes them. All values are overridable via ``MAYA_VOICE_*`` env vars.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

TurnDetection = Literal["stt", "vad", "realtime_llm", "manual"]


class VoiceConfig(BaseSettings):
    """Tunable parameters for the real-time voice pipeline."""

    model_config = SettingsConfigDict(
        env_prefix="MAYA_VOICE_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Latency ---------------------------------------------------------
    # Start generating a reply from the interim transcript, before the user's
    # turn is finalised — the single biggest perceived-latency win.
    preemptive_generation: bool = Field(default=True)
    # How long of a pause ends the user's turn. Lower = snappier but riskier
    # of cutting the caller off; higher = safer but slower.
    min_endpointing_delay: float = Field(default=0.4)
    max_endpointing_delay: float = Field(default=6.0)

    # --- Interruption / barge-in ----------------------------------------
    allow_interruptions: bool = Field(default=True)
    # Ignore very short blips (coughs, "mm-hmm") as interruptions.
    min_interruption_duration: float = Field(default=0.5)
    # VAD is available out of the box; the semantic turn-detector plugin
    # (livekit-plugins-turn-detector) is the upgrade path for fewer false ends.
    turn_detection: TurnDetection = Field(default="vad")

    # --- VAD sensitivity -------------------------------------------------
    vad_min_silence_duration: float = Field(default=0.4)
    vad_activation_threshold: float = Field(default=0.5)

    # --- Provider resilience (retries/timeouts) --------------------------
    stt_max_retry: int = Field(default=2)
    llm_max_retry: int = Field(default=2)
    tts_max_retry: int = Field(default=2)
    provider_timeout: float = Field(default=10.0)
    # Abort the session after this many consecutive unrecoverable provider errors.
    max_unrecoverable_errors: int = Field(default=5)

    # --- Tool execution --------------------------------------------------
    # Cancellation guard: a DB action that hangs must not freeze the call.
    tool_timeout_seconds: float = Field(default=8.0)

    # --- Dashboard realtime push (agent -> API internal endpoint) --------
    # Base URL of the API. When set, the agent pushes booking/callback events
    # so the dashboard updates instantly. Empty disables push (polling still
    # covers it). Not "voice" tuning, but the agent owns this integration.
    api_base_url: str = Field(default="http://localhost:8000")
    # Shares the API's unprefixed INTERNAL_EVENT_TOKEN so both sides match.
    internal_event_token: str | None = Field(
        default=None, validation_alias="INTERNAL_EVENT_TOKEN"
    )


@lru_cache(maxsize=1)
def get_voice_config() -> VoiceConfig:
    """Return the process-wide, cached voice configuration."""
    return VoiceConfig()
