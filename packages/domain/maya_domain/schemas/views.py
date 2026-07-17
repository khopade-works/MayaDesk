"""Read-only projection DTOs for the staff dashboard.

These join across aggregates (appointment + patient + slot) so the dashboard can
render a row without N+1 lookups. They are outputs only — never used for writes.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel

from maya_domain.models.enums import AppointmentStatus, CallbackPriority, CallbackStatus


class AppointmentView(BaseModel):
    """An appointment enriched with patient and slot details."""

    id: int
    patient_name: str
    patient_phone: str
    provider_name: str
    start_ts: datetime
    end_ts: datetime
    status: AppointmentStatus
    reason: str | None = None
    created_at: datetime


class CallbackView(BaseModel):
    """A callback request enriched with patient details (if identified)."""

    id: int
    patient_name: str | None = None
    patient_phone: str | None = None
    priority: CallbackPriority
    reason: str
    status: CallbackStatus
    created_at: datetime


class DashboardStats(BaseModel):
    """At-a-glance counts for the dashboard header."""

    appointments_total: int
    appointments_upcoming: int
    callbacks_pending: int
    emergencies_pending: int
