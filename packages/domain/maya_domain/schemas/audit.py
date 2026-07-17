"""Pydantic DTOs for the AuditLog aggregate."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AuditLogCreate(BaseModel):
    """Payload to create a new audit log entry."""

    actor: str = Field(min_length=1, max_length=255)
    action: str = Field(min_length=1, max_length=255)
    entity: str = Field(min_length=1, max_length=255)
    entity_id: int | None = None
    meta: dict[str, Any] | None = None

    @field_validator("actor", "action", "entity")
    @classmethod
    def validate_non_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value


class AuditLogUpdate(BaseModel):
    """Payload to partially update an existing audit log entry."""

    actor: str | None = Field(default=None, min_length=1, max_length=255)
    action: str | None = Field(default=None, min_length=1, max_length=255)
    entity: str | None = Field(default=None, min_length=1, max_length=255)
    entity_id: int | None = None
    meta: dict[str, Any] | None = None

    @field_validator("actor", "action", "entity")
    @classmethod
    def validate_non_blank(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("must not be blank")
        return value


class AuditLogRead(BaseModel):
    """Audit log entry as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    actor: str
    action: str
    entity: str
    entity_id: int | None = None
    meta: dict[str, Any] | None = None
    created_at: datetime
