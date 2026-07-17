"""Best-effort push of dashboard events from the agent to the API.

Fire-and-forget: emitting must never block or fail a live call. If the API is
unreachable, the event is dropped — the dashboard's polling still reflects the
committed database change, just a few seconds later.
"""

from __future__ import annotations

import asyncio
from typing import Any

import httpx

from maya_domain.core.logging import get_logger

from maya_agent.config import get_voice_config

_logger = get_logger("maya_agent.events")
_EMIT_TIMEOUT = 2.0

# Keep references so fire-and-forget tasks are not garbage-collected mid-flight.
_background: set[asyncio.Task[None]] = set()


async def _post_event(event_type: str, payload: dict[str, Any]) -> None:
    cfg = get_voice_config()
    if not cfg.api_base_url:
        return
    url = cfg.api_base_url.rstrip("/") + "/internal/events"
    headers = {}
    if cfg.internal_event_token:
        headers["X-Internal-Token"] = cfg.internal_event_token
    try:
        async with httpx.AsyncClient(timeout=_EMIT_TIMEOUT) as client:
            await client.post(url, json={"type": event_type, "payload": payload}, headers=headers)
    except Exception:  # noqa: BLE001 - best-effort; polling is the safety net
        _logger.warning("event.emit_failed", event_type=event_type)


def emit_dashboard_event(event_type: str, payload: dict[str, Any]) -> None:
    """Schedule a dashboard event push without awaiting it."""
    try:
        task = asyncio.create_task(_post_event(event_type, payload))
    except RuntimeError:
        # No running loop (e.g. called from sync context) — skip silently.
        return
    _background.add(task)
    task.add_done_callback(_background.discard)
