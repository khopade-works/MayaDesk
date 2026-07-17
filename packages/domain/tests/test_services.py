"""Integration tests for the Phase 4 use-case services against a real schema."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.core.errors import ConflictError, NotFoundError
from maya_domain.models.audit import AuditLog
from maya_domain.models.availability import Availability
from maya_domain.models.enums import AppointmentStatus, CallbackPriority, CallbackStatus
from maya_domain.models.callback import Callback
from maya_domain.repositories.appointment import AppointmentRepository
from maya_domain.repositories.availability import AvailabilityRepository
from maya_domain.services import (
    book_appointment,
    get_or_create_patient,
    list_open_slots,
    request_callback,
)
from maya_domain.services.dashboard_service import list_appointments

_NOW = datetime.now(timezone.utc)


async def _make_slot(
    session: AsyncSession,
    *,
    provider: str = "Dr. Rivera",
    offset_hours: int = 24,
    booked: bool = False,
) -> Availability:
    start = _NOW + timedelta(hours=offset_hours)
    slot = await AvailabilityRepository(session).create(
        provider_name=provider,
        start_ts=start,
        end_ts=start + timedelta(minutes=30),
        is_booked=booked,
    )
    return slot


async def _count(session: AsyncSession, model) -> int:
    return (await session.execute(select(func.count()).select_from(model))).scalar_one()


class TestAvailability:
    async def test_lists_unbooked_ordered_earliest_first(self, session: AsyncSession) -> None:
        await _make_slot(session, offset_hours=48)
        await _make_slot(session, offset_hours=24)
        slots = await list_open_slots(session)
        assert [s.provider_name for s in slots] == ["Dr. Rivera", "Dr. Rivera"]
        assert slots[0].start_ts < slots[1].start_ts

    async def test_excludes_booked_slots(self, session: AsyncSession) -> None:
        await _make_slot(session, offset_hours=24, booked=True)
        open_slot = await _make_slot(session, offset_hours=30)
        slots = await list_open_slots(session)
        assert [s.id for s in slots] == [open_slot.id]


class TestBooking:
    async def test_happy_path_books_slot_creates_patient_and_audits(
        self, session: AsyncSession
    ) -> None:
        slot = await _make_slot(session)
        result = await book_appointment(
            session,
            patient_name="Jane Doe",
            patient_phone="+15551234567",
            availability_id=slot.id,
            reason="Annual checkup",
        )
        assert result.appointment_id > 0
        assert result.patient_name == "Jane Doe"
        assert result.status == AppointmentStatus.scheduled.value

        refreshed = await AvailabilityRepository(session).get_or_404(slot.id)
        assert refreshed.is_booked is True

        audits = (
            await session.execute(
                select(AuditLog).where(AuditLog.action == "book_appointment")
            )
        ).scalars().all()
        assert len(audits) == 1 and audits[0].entity_id == result.appointment_id

    async def test_reuses_existing_patient_by_phone(self, session: AsyncSession) -> None:
        s1 = await _make_slot(session, offset_hours=24)
        s2 = await _make_slot(session, offset_hours=48)
        await book_appointment(
            session, patient_name="Jane Doe", patient_phone="+15551234567", availability_id=s1.id
        )
        await book_appointment(
            session, patient_name="Jane D", patient_phone="+15551234567", availability_id=s2.id
        )
        from maya_domain.models.patient import Patient

        assert await _count(session, Patient) == 1

    async def test_already_booked_raises_conflict(self, session: AsyncSession) -> None:
        slot = await _make_slot(session)
        await book_appointment(
            session, patient_name="A B", patient_phone="+15550000001", availability_id=slot.id
        )
        with pytest.raises(ConflictError):
            await book_appointment(
                session, patient_name="C D", patient_phone="+15550000002", availability_id=slot.id
            )

    async def test_missing_slot_raises_not_found(self, session: AsyncSession) -> None:
        with pytest.raises(NotFoundError):
            await book_appointment(
                session, patient_name="A B", patient_phone="+15550000003", availability_id=999999
            )


class TestCallback:
    async def test_creates_pending_callback_with_priority_and_audit(
        self, session: AsyncSession
    ) -> None:
        result = await request_callback(
            session,
            patient_name="Sam Lee",
            patient_phone="+15559990000",
            reason="Wants to discuss results",
            priority="urgent",
        )
        assert result.priority == CallbackPriority.urgent.value
        assert result.status == CallbackStatus.pending.value

        cb = (await session.execute(select(Callback))).scalar_one()
        assert cb.priority == CallbackPriority.urgent
        assert await _count(session, AuditLog) == 1

    async def test_emergency_priority_is_stored(self, session: AsyncSession) -> None:
        result = await request_callback(
            session,
            patient_name="Sam Lee",
            patient_phone="+15559990001",
            reason="Chest pain",
            priority="emergency",
        )
        assert result.priority == CallbackPriority.emergency.value


class TestGetOrCreatePatient:
    async def test_idempotent_by_phone(self, session: AsyncSession) -> None:
        p1 = await get_or_create_patient(session, full_name="Jane", phone="+15551112222")
        p2 = await get_or_create_patient(session, full_name="Jane Again", phone="+15551112222")
        assert p1.id == p2.id
        assert p1.full_name == "Jane"  # existing name preserved


class TestBookingRobustness:
    async def test_conflict_via_integrity_leaves_session_usable(
        self, session: AsyncSession
    ) -> None:
        """The unique-constraint (IntegrityError) path must not poison the session.

        Regression: a caught ConflictError inside a transaction must leave the
        session usable for further work (savepoint isolation).
        """
        slot_a = await _make_slot(session, offset_hours=24)
        slot_b = await _make_slot(session, offset_hours=25)

        # Orphan appointment on slot_a WITHOUT flipping is_booked -> forces the
        # IntegrityError path (not the is_booked pre-check).
        seed_patient = await get_or_create_patient(
            session, full_name="Seed", phone="+15550000000"
        )
        await AppointmentRepository(session).create(
            patient_id=seed_patient.id,
            availability_id=slot_a.id,
            status=AppointmentStatus.scheduled,
        )

        with pytest.raises(ConflictError):
            await book_appointment(
                session, patient_name="Alice", patient_phone="+15551110000", availability_id=slot_a.id
            )

        # Session survives the conflict: a subsequent booking still works.
        result = await book_appointment(
            session, patient_name="Bob", patient_phone="+15552220000", availability_id=slot_b.id
        )
        assert result.appointment_id > 0


class TestDashboardSearch:
    async def test_like_wildcards_are_escaped(self, session: AsyncSession) -> None:
        """Regression: '%'/'_' in search must be literal, not LIKE wildcards."""
        slot = await _make_slot(session)
        await book_appointment(
            session, patient_name="Jane Smith", patient_phone="+15551234567", availability_id=slot.id
        )

        assert len(await list_appointments(session, search="jane")) == 1
        assert len(await list_appointments(session, search="SMITH")) == 1  # case-insensitive
        assert len(await list_appointments(session, search="%")) == 0  # not match-all
        assert len(await list_appointments(session, search="_")) == 0
        assert len(await list_appointments(session)) == 1  # unfiltered
