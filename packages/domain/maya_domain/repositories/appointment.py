"""Repository for :class:`Appointment` aggregates."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from maya_domain.models.appointment import Appointment
from maya_domain.models.enums import AppointmentStatus
from maya_domain.repositories.base import BaseRepository


class AppointmentRepository(BaseRepository[Appointment]):
    """Data access for scheduled appointments."""

    model = Appointment

    async def list_by_patient(self, patient_id: int) -> Sequence[Appointment]:
        """Return all appointments for the given patient."""
        stmt = select(Appointment).where(Appointment.patient_id == patient_id)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_by_status(self, status: AppointmentStatus) -> Sequence[Appointment]:
        """Return all appointments with the given status."""
        stmt = select(Appointment).where(Appointment.status == status)
        result = await self.session.execute(stmt)
        return result.scalars().all()
