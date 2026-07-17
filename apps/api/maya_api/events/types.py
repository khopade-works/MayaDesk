"""Event payloads broadcast to the dashboard."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

DashboardEventType = Literal["appointment_booked", "callback_created", "emergency"]


class DashboardEvent(BaseModel):
    """A realtime notification pushed to connected dashboards."""

    type: DashboardEventType
    payload: dict[str, Any] = Field(default_factory=dict)
