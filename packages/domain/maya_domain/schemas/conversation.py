"""Pydantic DTOs for the ConversationHistory aggregate."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from maya_domain.models.enums import ConversationRole


class ConversationMessageCreate(BaseModel):
    """Payload to create a new conversation turn."""

    call_log_id: int
    role: ConversationRole
    content: str = Field(min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("content must not be blank")
        return value


class ConversationMessageUpdate(BaseModel):
    """Payload to partially update an existing conversation turn."""

    call_log_id: int | None = None
    role: ConversationRole | None = None
    content: str | None = Field(default=None, min_length=1)

    @field_validator("content")
    @classmethod
    def validate_content(cls, value: str | None) -> str | None:
        if value is not None and not value.strip():
            raise ValueError("content must not be blank")
        return value


class ConversationMessageRead(BaseModel):
    """Conversation turn as returned from the API/database."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    call_log_id: int
    role: ConversationRole
    content: str
    created_at: datetime
