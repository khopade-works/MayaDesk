"""Patient aggregate root."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base
from maya_domain.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from maya_domain.models.appointment import Appointment
    from maya_domain.models.callback import Callback
    from maya_domain.models.call_log import CallLog


class Patient(TimestampMixin, Base):
    """A person known to the practice, identified by phone number."""

    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)

    appointments: Mapped[list[Appointment]] = relationship(back_populates="patient")
    callbacks: Mapped[list[Callback]] = relationship(back_populates="patient")
    call_logs: Mapped[list[CallLog]] = relationship(back_populates="patient")
