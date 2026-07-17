"""Conversation transcript turns belonging to a call."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base
from maya_domain.models.enums import ConversationRole

if TYPE_CHECKING:
    from maya_domain.models.call_log import CallLog


class ConversationHistory(Base):
    """A single utterance within a call's transcript."""

    __tablename__ = "conversation_history"

    id: Mapped[int] = mapped_column(primary_key=True)
    call_log_id: Mapped[int] = mapped_column(
        ForeignKey("call_logs.id"),
        index=True,
        nullable=False,
    )
    role: Mapped[ConversationRole] = mapped_column(Enum(ConversationRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    call_log: Mapped[CallLog] = relationship(back_populates="messages")
