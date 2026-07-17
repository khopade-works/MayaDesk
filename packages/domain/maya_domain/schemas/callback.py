"""Pydantic DTOs for the Callback aggregate."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from maya_domain.models.enums import CallbackPriority, CallbackStatus


class CallbackCreate(BaseModel):
    """Payload to create a new callback request."""

    patient_id: int | None = None
    priority: CallbackPriority
    reason: str = Field(min_length=1)
    status: CallbackStatus = CallbackStatus.pending

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("reason must not be blank")
        return value


class CallbackUpdate(BaseModel):
    """Payload to partially update an existing callback request."""

    patient_id: int | None = None
    priority: CallbackPriority | None = None
    reason: str | None = Field(default=None, min_length=1)
    status: CallbackStatus | None = None

    @field_validator("reason")
    @classmethod
    def validate_reason(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("reason must not be blank")
        return value


class CallbackRead(BaseModel):
    """Callback request as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: int | None = None
    priority: CallbackPriority
    reason: str
    status: CallbackStatus
    created_at: datetime
    updated_at: datetime
