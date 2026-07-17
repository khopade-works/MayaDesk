"""Database seed script for MayaDesk local/dev environments.

Creates baseline providers, availability slots, and sample patients, then
exercises the real booking and callback service layer so seeded appointments
and callbacks come with valid audit trails and booked slots -- exactly what
production traffic would produce.

Run via::

    python -m maya_domain.seed

Idempotent by default: if any availability rows already exist, the script
prints a message and exits without writing more data. Set ``MAYA_SEED_FORCE=1``
to seed additional data on top of an existing database.
"""

from __future__ import annotations

import asyncio
import os
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import func, select

from maya_domain import models
from maya_domain.core.logging import get_logger
from maya_domain.database.engine import engine
from maya_domain.database.session import AsyncSessionLocal
from maya_domain.database.uow import unit_of_work
from maya_domain.repositories.availability import AvailabilityRepository
from maya_domain.services import book_appointment, request_callback

logger = get_logger(__name__)

_PROVIDERS: list[str] = ["Dr. Rivera", "Dr. Chen", "Dr. Okafor"]

_PATIENTS: list[tuple[str, str]] = [
    ("Maria Gonzalez", "+14155550101"),
    ("James Whitfield", "+14155550102"),
    ("Aisha Bello", "+14155550103"),
    ("Tom Nakamura", "+14155550104"),
]

_BUSINESS_START = time(9, 0)
_BUSINESS_END = time(16, 0)
_SLOT_MINUTES = 30
_DAYS_AHEAD = 7
_BOOKING_COUNT = 5


def _business_days(start: date, calendar_days: int) -> list[date]:
    """Return the weekdays (Mon-Fri) within the next ``calendar_days`` days."""
    return [
        day
        for offset in range(calendar_days)
        if (day := start + timedelta(days=offset)).weekday() < 5
    ]


def _slot_starts(day: date) -> list[datetime]:
    """Return the 30-minute slot start times for ``day`` within business hours."""
    starts: list[datetime] = []
    current = datetime.combine(day, _BUSINESS_START, tzinfo=timezone.utc)
    end = datetime.combine(day, _BUSINESS_END, tzinfo=timezone.utc)
    step = timedelta(minutes=_SLOT_MINUTES)
    while current + step <= end:
        starts.append(current)
        current += step
    return starts


async def _already_seeded() -> int:
    """Return the number of existing availability rows."""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(func.count()).select_from(models.Availability)
        )
        return int(result.scalar_one())


async def _seed_availability() -> list[int]:
    """Create every provider's availability slots for the next business week.

    Returns the ids of every slot created, in creation order.
    """
    today = datetime.now(timezone.utc).date()
    days = _business_days(today, _DAYS_AHEAD)

    slot_ids: list[int] = []
    async with unit_of_work() as session:
        repo = AvailabilityRepository(session)
        for provider_name in _PROVIDERS:
            for day in days:
                for start_ts in _slot_starts(day):
                    slot = await repo.create(
                        provider_name=provider_name,
                        start_ts=start_ts,
                        end_ts=start_ts + timedelta(minutes=_SLOT_MINUTES),
                        is_booked=False,
                    )
                    slot_ids.append(slot.id)

    logger.info("seed.availability_created", count=len(slot_ids))
    return slot_ids


async def _seed_bookings(slot_ids: list[int]) -> int:
    """Book a handful of the freshly created slots via the real booking service."""
    booking_count = min(_BOOKING_COUNT, len(slot_ids))
    if booking_count == 0:
        return 0
    step = max(len(slot_ids) // booking_count, 1)
    chosen = [slot_ids[i * step] for i in range(booking_count)]

    booked = 0
    for i, availability_id in enumerate(chosen):
        patient_name, patient_phone = _PATIENTS[i % len(_PATIENTS)]
        async with unit_of_work() as session:
            await book_appointment(
                session,
                patient_name=patient_name,
                patient_phone=patient_phone,
                availability_id=availability_id,
                reason="Annual checkup",
            )
        booked += 1

    logger.info("seed.appointments_booked", count=booked)
    return booked


async def _seed_callbacks() -> int:
    """Create sample callback requests via the real callback service."""
    requests = [
        (_PATIENTS[0], "Reschedule request", models.CallbackPriority.normal),
        (
            _PATIENTS[1],
            "Question about prescription refill",
            models.CallbackPriority.normal,
        ),
        (_PATIENTS[2], "Insurance verification needed", models.CallbackPriority.urgent),
        (_PATIENTS[3], "Chest pain", models.CallbackPriority.emergency),
    ]

    created = 0
    for (patient_name, patient_phone), reason, priority in requests:
        async with unit_of_work() as session:
            await request_callback(
                session,
                patient_name=patient_name,
                patient_phone=patient_phone,
                reason=reason,
                priority=priority,
            )
        created += 1

    logger.info("seed.callbacks_created", count=created)
    return created


async def _summary() -> dict[str, int]:
    """Return row counts for every table the seed script touches."""
    tables = (
        ("availability", models.Availability),
        ("patients", models.Patient),
        ("appointments", models.Appointment),
        ("callbacks", models.Callback),
        ("audit_logs", models.AuditLog),
    )
    async with AsyncSessionLocal() as session:
        counts: dict[str, int] = {}
        for label, model in tables:
            result = await session.execute(select(func.count()).select_from(model))
            counts[label] = int(result.scalar_one())
        return counts


async def seed() -> None:
    """Populate the configured database with sample development data."""
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

    force = os.environ.get("MAYA_SEED_FORCE") == "1"
    existing = await _already_seeded()
    if existing > 0 and not force:
        print(
            f"already seeded ({existing} slots); "
            "pass MAYA_SEED_FORCE=1 to add more"
        )
        return

    slot_ids = await _seed_availability()
    booked = await _seed_bookings(slot_ids)
    callbacks = await _seed_callbacks()

    counts = await _summary()
    print(
        "seed complete: "
        f"{counts['availability']} availability slots, "
        f"{counts['patients']} patients, "
        f"{booked} appointments booked ({counts['appointments']} total), "
        f"{callbacks} callbacks created ({counts['callbacks']} total)"
    )


def main() -> None:
    """Entry point for ``python -m maya_domain.seed``."""
    asyncio.run(seed())


if __name__ == "__main__":
    main()
