"""Edge TTS provider — a custom LiveKit ``tts.TTS`` backed by Microsoft Edge TTS.

Edge TTS is *not* an official LiveKit plugin, so we adapt it to the framework's
``tts.TTS`` contract. ``AgentSession`` accepts any ``tts.TTS``, which makes this
the swap point for production voices (Cartesia, Deepgram Aura, ElevenLabs): build
a different provider in :mod:`maya_agent.session` and nothing else changes.

Edge TTS streams MP3. We hand those bytes to the framework's ``AudioEmitter``
with an ``audio/mp3`` mime type; its PyAV-backed decoder turns them into PCM
frames — the same path the shipped OpenAI plugin uses for MP3 output.

Operational note: Edge TTS is an unofficial endpoint with no SLA or BAA. It is a
dev/demo default only; do not depend on it for production or real PHI.
"""

from __future__ import annotations

import edge_tts

from livekit.agents import APIConnectionError, APIConnectOptions, tts, utils
from livekit.agents.types import DEFAULT_API_CONNECT_OPTIONS

# Edge TTS emits 24 kHz mono MP3.
_SAMPLE_RATE = 24000
_NUM_CHANNELS = 1
_DEFAULT_VOICE = "en-US-AriaNeural"


class EdgeTTS(tts.TTS):
    """LiveKit TTS adapter for Microsoft Edge TTS.

    :param voice: Edge TTS voice short name (e.g. ``en-US-AriaNeural``).
    """

    def __init__(self, *, voice: str = _DEFAULT_VOICE) -> None:
        super().__init__(
            capabilities=tts.TTSCapabilities(streaming=False),
            sample_rate=_SAMPLE_RATE,
            num_channels=_NUM_CHANNELS,
        )
        self._voice = voice

    def synthesize(
        self,
        text: str,
        *,
        conn_options: APIConnectOptions = DEFAULT_API_CONNECT_OPTIONS,
    ) -> _EdgeChunkedStream:
        return _EdgeChunkedStream(tts=self, input_text=text, conn_options=conn_options)


class _EdgeChunkedStream(tts.ChunkedStream):
    """One-shot synthesis of a single utterance into the output emitter."""

    def __init__(
        self,
        *,
        tts: EdgeTTS,
        input_text: str,
        conn_options: APIConnectOptions,
    ) -> None:
        super().__init__(tts=tts, input_text=input_text, conn_options=conn_options)
        self._tts: EdgeTTS = tts

    async def _run(self, output_emitter: tts.AudioEmitter) -> None:
        output_emitter.initialize(
            request_id=utils.shortuuid(),
            sample_rate=self._tts.sample_rate,
            num_channels=self._tts.num_channels,
            mime_type="audio/mp3",
        )

        try:
            communicate = edge_tts.Communicate(self.input_text, self._tts._voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio" and chunk.get("data"):
                    output_emitter.push(chunk["data"])
            output_emitter.flush()
        except Exception as exc:  # noqa: BLE001 — surface as a framework API error
            raise APIConnectionError() from exc
