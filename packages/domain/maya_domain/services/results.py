"""Result DTOs returned by services to their callers (agent tools, API).

These are deliberately small and presentation-friendly: they carry exactly what
a caller needs to confirm an action to the patient, without leaking ORM objects
across the transaction boundary.
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class OpenSlot(BaseModel):
    """A bookable availability slot offered to the patient."""

    id: int
    provider_name: str
    start_ts: datetime
    end_ts: datetime


class BookingResult(BaseModel):
    """Confirmation of a completed booking."""

    appointment_id: int
    patient_name: str
    provider_name: str
    start_ts: datetime
    status: str


class CallbackResult(BaseModel):
    """Confirmation of a logged callback request."""

    callback_id: int
    priority: str
    status: str
