"""Pydantic DTOs for the Patient aggregate."""

from __future__ import annotations

import re
from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

_PHONE_PATTERN = re.compile(r"^\+?[1-9]\d{6,14}$")


class PatientBase(BaseModel):
    """Fields shared by patient create/update payloads."""

    full_name: str = Field(min_length=1, max_length=255)
    phone: str = Field(min_length=7, max_length=32)
    date_of_birth: date | None = None
    email: EmailStr | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str) -> str:
        if not _PHONE_PATTERN.match(value):
            raise ValueError(
                "phone must be a valid E.164-ish number, e.g. +15551234567"
            )
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class PatientCreate(PatientBase):
    """Payload to create a new patient."""


class PatientUpdate(BaseModel):
    """Payload to partially update an existing patient."""

    full_name: str | None = Field(default=None, min_length=1, max_length=255)
    phone: str | None = Field(default=None, min_length=7, max_length=32)
    date_of_birth: date | None = None
    email: EmailStr | None = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is not None and not _PHONE_PATTERN.match(value):
            raise ValueError(
                "phone must be a valid E.164-ish number, e.g. +15551234567"
            )
        return value

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, value: date | None) -> date | None:
        if value is not None and value > date.today():
            raise ValueError("date_of_birth cannot be in the future")
        return value


class PatientRead(PatientBase):
    """Patient as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
