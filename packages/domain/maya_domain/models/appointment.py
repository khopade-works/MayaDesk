"""Appointment aggregate binding a patient to an availability slot."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Enum, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from maya_domain.database.base import Base
from maya_domain.models.enums import AppointmentStatus
from maya_domain.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from maya_domain.models.availability import Availability
    from maya_domain.models.patient import Patient


class Appointment(TimestampMixin, Base):
    """A scheduled visit occupying exactly one availability slot."""

    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[int] = mapped_column(
        ForeignKey("patients.id"),
        index=True,
        nullable=False,
    )
    availability_id: Mapped[int] = mapped_column(
        ForeignKey("availability.id"),
        unique=True,
        nullable=False,
    )
    status: Mapped[AppointmentStatus] = mapped_column(
        Enum(AppointmentStatus),
        default=AppointmentStatus.scheduled,
        index=True,
        nullable=False,
    )
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    patient: Mapped[Patient] = relationship(back_populates="appointments")
    availability: Mapped[Availability] = relationship(back_populates="appointment")
