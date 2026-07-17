"""Provider availability slots that can be booked into appointments."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base

if TYPE_CHECKING:
    from maya_domain.models.appointment import Appointment


class Availability(Base):
    """A bookable time window for a named provider."""

    __tablename__ = "availability"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_name: Mapped[str] = mapped_column(String(255), nullable=False)
    start_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_ts: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_booked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    appointment: Mapped[Appointment | None] = relationship(
        back_populates="availability",
        uselist=False,
    )

    __table_args__ = (
        Index("ix_availability_start_ts_is_booked", "start_ts", "is_booked"),
        CheckConstraint("end_ts > start_ts", name="end_after_start"),
    )
