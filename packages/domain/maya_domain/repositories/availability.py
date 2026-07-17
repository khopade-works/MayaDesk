"""Repository for :class:`Availability` aggregates."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from sqlalchemy import select

from maya_domain.models.availability import Availability
from maya_domain.repositories.base import BaseRepository


class AvailabilityRepository(BaseRepository[Availability]):
    """Data access for provider availability slots."""

    model = Availability

    async def find_open_slots(
        self, start_from: datetime, start_to: datetime
    ) -> Sequence[Availability]:
        """Return unbooked slots starting within ``[start_from, start_to]``, earliest first."""
        stmt = (
            select(Availability)
            .where(
                Availability.is_booked.is_(False),
                Availability.start_ts >= start_from,
                Availability.start_ts <= start_to,
            )
            .order_by(Availability.start_ts)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def mark_booked(self, availability: Availability) -> Availability:
        """Mark ``availability`` as booked and flush."""
        availability.is_booked = True
        await self.session.flush()
        return availability
