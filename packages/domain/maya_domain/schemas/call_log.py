"""Pydantic DTOs for the CallLog aggregate."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from maya_domain.models.enums import CallOutcome


class CallLogCreate(BaseModel):
    """Payload to create a new call log."""

    room_name: str = Field(min_length=1, max_length=255)
    patient_id: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    outcome: CallOutcome | None = None

    @field_validator("room_name")
    @classmethod
    def validate_room_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("room_name must not be blank")
        return value


class CallLogUpdate(BaseModel):
    """Payload to partially update an existing call log."""

    room_name: str | None = Field(default=None, min_length=1, max_length=255)
    patient_id: int | None = None
    started_at: datetime | None = None
    ended_at: datetime | None = None
    outcome: CallOutcome | None = None

    @field_validator("room_name")
    @classmethod
    def validate_room_name(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("room_name must not be blank")
        return value


class CallLogRead(BaseModel):
    """Call log as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    room_name: str
    patient_id: int | None = None
    started_at: datetime
    ended_at: datetime | None = None
    outcome: CallOutcome | None = None
    created_at: datetime
