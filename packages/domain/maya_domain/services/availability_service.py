"""Availability use case: list bookable slots for the patient to choose from."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.repositories.availability import AvailabilityRepository
from maya_domain.services.results import OpenSlot

_DEFAULT_WINDOW = timedelta(days=14)
_MAX_SLOTS = 20


async def list_open_slots(
    session: AsyncSession,
    *,
    start_from: datetime | None = None,
    start_to: datetime | None = None,
) -> list[OpenSlot]:
    """Return unbooked slots within the window, earliest first (capped)."""
    now = datetime.now(timezone.utc)
    start_from = start_from or now
    start_to = start_to or (start_from + _DEFAULT_WINDOW)

    repo = AvailabilityRepository(session)
    slots = await repo.find_open_slots(start_from, start_to)
    return [
        OpenSlot(
            id=slot.id,
            provider_name=slot.provider_name,
            start_ts=slot.start_ts,
            end_ts=slot.end_ts,
        )
        for slot in slots[:_MAX_SLOTS]
    ]
