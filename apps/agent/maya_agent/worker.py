"""Maya voice worker — the LiveKit Agents entrypoint.

Runs a LiveKit Agents worker. On each dispatched call the worker connects to the
room, composes the voice pipeline (Silero VAD + Groq Whisper STT + Groq Llama LLM
+ Edge TTS), starts an ``AgentSession`` driving :class:`MayaAgent`, and opens the
conversation with a greeting.

Silero's model is loaded once per worker process in :func:`prewarm` (it is a
blocking load) and reused across calls, keeping per-call setup off the hot path.
"""

from __future__ import annotations

from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.plugins import silero

from maya_domain.core.logging import get_logger

from maya_agent.agent import MayaAgent
from maya_agent.config import get_voice_config
from maya_agent.session import build_session

_logger = get_logger("maya_agent.worker")

_GREETING = (
    "Greet the caller warmly as Maya from the clinic and ask how you can help today. "
    "Keep it to one short sentence."
)


def prewarm(proc: JobProcess) -> None:
    """Load the Silero VAD once per worker process, tuned from voice config."""
    voice = get_voice_config()
    proc.userdata["vad"] = silero.VAD.load(
        min_silence_duration=voice.vad_min_silence_duration,
        activation_threshold=voice.vad_activation_threshold,
    )


async def entrypoint(ctx: JobContext) -> None:
    """Handle one dispatched call: connect, start the session, greet the caller."""
    await ctx.connect()
    _logger.info("call.connected", room=ctx.room.name)

    session: AgentSession = build_session(vad=ctx.proc.userdata["vad"])
    agent: Agent = MayaAgent()

    await session.start(room=ctx.room, agent=agent)
    await session.generate_reply(instructions=_GREETING)


def main() -> None:
    """Run the worker (invoked by ``python -m maya_agent.worker``)."""
    load_dotenv()
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))


if __name__ == "__main__":
    main()
