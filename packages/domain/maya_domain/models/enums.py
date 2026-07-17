"""Shared enumerations used across MayaDesk ORM models.

Each enum is a ``str`` mix-in so members compare equal to their wire value and
serialise cleanly, while still being stored as a SQLAlchemy ``Enum`` column.
"""

from __future__ import annotations

import enum


class AppointmentStatus(str, enum.Enum):
    """Lifecycle of a booked appointment."""

    scheduled = "scheduled"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"
    no_show = "no_show"


class CallbackPriority(str, enum.Enum):
    """Urgency of a requested callback."""

    normal = "normal"
    urgent = "urgent"
    emergency = "emergency"


class CallbackStatus(str, enum.Enum):
    """Handling state of a callback request."""

    pending = "pending"
    in_progress = "in_progress"
    resolved = "resolved"


class CallOutcome(str, enum.Enum):
    """Terminal outcome of a voice call."""

    completed = "completed"
    dropped = "dropped"
    escalated = "escalated"
    booked = "booked"


class ConversationRole(str, enum.Enum):
    """Author role of a conversation turn."""

    patient = "patient"
    assistant = "assistant"
    system = "system"
    tool = "tool"
