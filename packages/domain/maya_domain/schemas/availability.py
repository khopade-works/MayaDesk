"""Pydantic DTOs for the Availability aggregate."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class AvailabilityBase(BaseModel):
    """Fields shared by availability create/update payloads."""

    provider_name: str = Field(min_length=1, max_length=255)
    start_ts: datetime
    end_ts: datetime
    is_booked: bool = False

    @model_validator(mode="after")
    def validate_time_range(self) -> "AvailabilityBase":
        if self.end_ts <= self.start_ts:
            raise ValueError("end_ts must be after start_ts")
        return self


class AvailabilityCreate(AvailabilityBase):
    """Payload to create a new availability slot."""


class AvailabilityUpdate(BaseModel):
    """Payload to partially update an existing availability slot."""

    provider_name: str | None = Field(default=None, min_length=1, max_length=255)
    start_ts: datetime | None = None
    end_ts: datetime | None = None
    is_booked: bool | None = None

    @model_validator(mode="after")
    def validate_time_range(self) -> "AvailabilityUpdate":
        if (
            self.start_ts is not None
            and self.end_ts is not None
            and self.end_ts <= self.start_ts
        ):
            raise ValueError("end_ts must be after start_ts")
        return self


class AvailabilityRead(AvailabilityBase):
    """Availability slot as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
