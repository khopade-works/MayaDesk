"""Dashboard WebSocket gateway.

Streams realtime events to connected staff dashboards. Delivery is best-effort
and stateless: on connect the client should also fetch a snapshot over REST, then
apply pushes on top (the frontend invalidates its React Query cache per event).
"""

from __future__ import annotations

import asyncio
import contextlib

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from maya_domain.core.logging import get_logger

from maya_api.events import get_event_bus

router = APIRouter()
_logger = get_logger("maya_api.ws.dashboard")


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket) -> None:
    await websocket.accept()
    bus = get_event_bus()

    # Drain any client-sent frames so a client-side close is detected promptly.
    async def _consume_incoming() -> None:
        with contextlib.suppress(Exception):
            while True:
                await websocket.receive_text()

    # Register the subscription synchronously *before* greeting, so no event
    # published between accept and subscribe can be missed.
    queue = bus.add_subscriber()
    reader = asyncio.create_task(_consume_incoming())
    try:
        await websocket.send_json({"type": "connected", "payload": {}})
        while True:
            event = await queue.get()
            await websocket.send_json(event)
    except WebSocketDisconnect:
        pass
    except Exception:  # noqa: BLE001 - client vanished mid-send; nothing to do
        _logger.debug("ws.dashboard.send_failed")
    finally:
        bus.remove_subscriber(queue)
        reader.cancel()
        with contextlib.suppress(Exception):
            await reader
