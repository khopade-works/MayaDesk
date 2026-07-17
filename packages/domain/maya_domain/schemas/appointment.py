"""Pydantic DTOs for the Appointment aggregate."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from maya_domain.models.enums import AppointmentStatus


class AppointmentCreate(BaseModel):
    """Payload to create a new appointment."""

    patient_id: int
    availability_id: int
    status: AppointmentStatus = AppointmentStatus.scheduled
    reason: str | None = Field(default=None, max_length=10_000)


class AppointmentUpdate(BaseModel):
    """Payload to partially update an existing appointment."""

    patient_id: int | None = None
    availability_id: int | None = None
    status: AppointmentStatus | None = None
    reason: str | None = Field(default=None, max_length=10_000)


class AppointmentRead(BaseModel):
    """Appointment as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int
    availability_id: int
    status: AppointmentStatus
    reason: str | None = None
    created_at: datetime
    updated_at: datetime
