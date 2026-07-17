"""Per-call records for voice sessions."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base
from maya_domain.models.enums import CallOutcome

if TYPE_CHECKING:
    from maya_domain.models.conversation import ConversationHistory
    from maya_domain.models.patient import Patient


class CallLog(Base):
    """A single voice call, its lifecycle timestamps, and its transcript."""

    __tablename__ = "call_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    room_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    patient_id: Mapped[int | None] = mapped_column(
        ForeignKey("patients.id"),
        index=True,
        nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    outcome: Mapped[CallOutcome | None] = mapped_column(Enum(CallOutcome), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    patient: Mapped[Patient | None] = relationship(back_populates="call_logs")
    messages: Mapped[list[ConversationHistory]] = relationship(
        back_populates="call_log",
        cascade="all, delete-orphan",
    )
