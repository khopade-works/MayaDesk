"""Repository for :class:`Patient` aggregates."""

from __future__ import annotations

from sqlalchemy import select

from maya_domain.models.patient import Patient
from maya_domain.repositories.base import BaseRepository


class PatientRepository(BaseRepository[Patient]):
    """Data access for patients, keyed by phone number."""

    model = Patient

    async def get_by_phone(self, phone: str) -> Patient | None:
        """Return the patient with the given phone number, or ``None``."""
        stmt = select(Patient).where(Patient.phone == phone)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
