"""Callback requests captured when a live booking cannot complete."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base
from maya_domain.models.enums import CallbackPriority, CallbackStatus
from maya_domain.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from maya_domain.models.patient import Patient


class Callback(TimestampMixin, Base):
    """A request to call a patient back, possibly before identification."""

    __tablename__ = "callbacks"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id"),
        index=True,
        nullable=True,
    )
    priority: Mapped[CallbackPriority] = mapped_column(
        Enum(CallbackPriority),
        nullable=False,
    )
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[CallbackStatus] = mapped_column(
        Enum(CallbackStatus),
        default=CallbackStatus.pending,
        nullable=False,
    )

    patient: Mapped[Patient | None] = relationship(back_populates="callbacks")

    __table_args__ = (
        Index("ix_callbacks_status_priority", "status", "priority"),
    )
