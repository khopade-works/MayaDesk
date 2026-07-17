"""Internal event ingress — how the voice agent notifies the dashboard.

The agent runs in a separate process, so after it commits a booking or callback
it POSTs a small event here; we republish it on the in-process bus, which the
WebSocket gateway fans out to connected dashboards. Guarded by a shared secret
when ``INTERNAL_EVENT_TOKEN`` is configured.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header, HTTPException

from maya_domain.config import get_settings

from maya_api.events import DashboardEvent, get_event_bus

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/events", status_code=202)
async def publish_event(
    event: DashboardEvent,
    x_internal_token: Annotated[str | None, Header()] = None,
) -> dict[str, bool]:
    """Accept an event from a trusted internal caller and broadcast it."""
    expected = get_settings().internal_event_token
    if expected and x_internal_token != expected:
        raise HTTPException(status_code=401, detail="Invalid internal token.")

    await get_event_bus().publish(event.model_dump())
    return {"accepted": True}
