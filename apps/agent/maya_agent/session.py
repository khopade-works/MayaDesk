"""Voice-pipeline assembly for the Maya agent.

Builds the STT / LLM / TTS components from validated settings and composes them
into an ``AgentSession``. Each provider is constructed behind a small factory so
the choice is swappable and the required configuration is validated in one place
(explicit dependency injection rather than ambient environment reads).
"""

from __future__ import annotations

from livekit.agents import (
    AgentSession,
    EndpointingOptions,
    InterruptionOptions,
    PreemptiveGenerationOptions,
    TurnHandlingOptions,
)
from livekit.agents.types import APIConnectOptions
from livekit.agents.vad import VAD
from livekit.agents.voice.agent_session import SessionConnectOptions
from livekit.plugins import groq

from maya_domain.config import Settings, get_settings
from maya_domain.core.errors import ConfigurationError

from maya_agent.config import VoiceConfig, get_voice_config
from maya_agent.tts import EdgeTTS


def _require_groq_key(settings: Settings) -> str:
    if not settings.groq_api_key:
        raise ConfigurationError("GROQ_API_KEY is not configured; the voice agent cannot start.")
    return settings.groq_api_key


def build_stt(settings: Settings | None = None) -> groq.STT:
    """Groq Whisper speech-to-text, model from settings."""
    settings = settings or get_settings()
    return groq.STT(
        model=settings.groq_stt_model,
        api_key=_require_groq_key(settings),
        language="en",
    )


def build_llm(settings: Settings | None = None) -> groq.LLM:
    """Groq Llama dialogue model, id from settings."""
    settings = settings or get_settings()
    return groq.LLM(
        model=settings.groq_llm_model,
        api_key=_require_groq_key(settings),
    )


def build_tts(settings: Settings | None = None) -> EdgeTTS:
    """Text-to-speech provider. Edge TTS today; swap here for a production voice."""
    return EdgeTTS()


def _build_conn_options(voice: VoiceConfig) -> SessionConnectOptions:
    """Per-component retry/timeout policy for STT, LLM, and TTS."""
    return SessionConnectOptions(
        stt_conn_options=APIConnectOptions(
            max_retry=voice.stt_max_retry, timeout=voice.provider_timeout
        ),
        llm_conn_options=APIConnectOptions(
            max_retry=voice.llm_max_retry, timeout=voice.provider_timeout
        ),
        tts_conn_options=APIConnectOptions(
            max_retry=voice.tts_max_retry, timeout=voice.provider_timeout
        ),
        max_unrecoverable_errors=voice.max_unrecoverable_errors,
    )


def _build_turn_handling(voice: VoiceConfig) -> TurnHandlingOptions:
    """Group turn-detection, endpointing, interruption, and preemption tuning.

    Uses the current ``turn_handling`` API rather than the flat AgentSession
    kwargs, which are deprecated for removal in livekit-agents v2.0.
    """
    return TurnHandlingOptions(
        turn_detection=voice.turn_detection,
        endpointing=EndpointingOptions(
            min_delay=voice.min_endpointing_delay,
            max_delay=voice.max_endpointing_delay,
        ),
        interruption=InterruptionOptions(
            enabled=voice.allow_interruptions,
            min_duration=voice.min_interruption_duration,
        ),
        preemptive_generation=PreemptiveGenerationOptions(
            enabled=voice.preemptive_generation,
        ),
    )


def build_session(
    vad: VAD,
    settings: Settings | None = None,
    voice: VoiceConfig | None = None,
) -> AgentSession:
    """Compose the tuned voice pipeline into an ``AgentSession``.

    :param vad: A preloaded Silero VAD (loaded once per worker in prewarm).
    """
    settings = settings or get_settings()
    voice = voice or get_voice_config()
    return AgentSession(
        vad=vad,
        stt=build_stt(settings),
        llm=build_llm(settings),
        tts=build_tts(settings),
        turn_handling=_build_turn_handling(voice),
        conn_options=_build_conn_options(voice),
    )
