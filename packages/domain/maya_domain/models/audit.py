"""Append-only audit trail of significant actions."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from maya_domain.database.base import Base


class AuditLog(Base):
    """A recorded action taken by an actor against some entity.

    The free-form payload column is named ``meta`` at both the Python and SQL
    level because ``metadata`` is reserved on the declarative ``Base``.
    """

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    actor: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_id: Mapped[int | None] = mapped_column(nullable=True)
    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        index=True,
        nullable=False,
    )
