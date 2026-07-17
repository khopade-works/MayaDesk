"""Integration tests for maya_domain.repositories against a real SQLite schema."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.core.errors import NotFoundError
from maya_domain.models.enums import (
    AppointmentStatus,
    CallbackPriority,
    CallbackStatus,
    CallOutcome,
    ConversationRole,
)
from maya_domain.repositories import (
    AppointmentRepository,
    AuditRepository,
    AvailabilityRepository,
    CallbackRepository,
    CallLogRepository,
    ConversationRepository,
    PatientRepository,
)

UTC = timezone.utc


def _dt(minutes_from_now: int) -> datetime:
    return datetime.now(UTC) + timedelta(minutes=minutes_from_now)


# --- Patient -----------------------------------------------------------


@pytest.mark.asyncio
async def test_patient_create_and_get_roundtrip(session: AsyncSession) -> None:
    repo = PatientRepository(session)
    created = await repo.create(full_name="Ada Lovelace", phone="+15551234567")

    fetched = await repo.get(created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.phone == "+15551234567"


@pytest.mark.asyncio
async def test_patient_get_by_phone(session: AsyncSession) -> None:
    repo = PatientRepository(session)
    await repo.create(full_name="Grace Hopper", phone="+15559876543")

    found = await repo.get_by_phone("+15559876543")
    missing = await repo.get_by_phone("+10000000000")

    assert found is not None
    assert found.full_name == "Grace Hopper"
    assert missing is None


@pytest.mark.asyncio
async def test_patient_unique_phone_conflict(session: AsyncSession) -> None:
    repo = PatientRepository(session)
    await repo.create(full_name="Alan Turing", phone="+15550001111")

    with pytest.raises(IntegrityError):
        await repo.create(full_name="Someone Else", phone="+15550001111")

    await session.rollback()


# --- Availability --------------------------------------------------------


@pytest.mark.asyncio
async def test_availability_create_and_get_roundtrip(session: AsyncSession) -> None:
    repo = AvailabilityRepository(session)
    created = await repo.create(
        provider_name="Dr. Smith",
        start_ts=_dt(60),
        end_ts=_dt(90),
    )

    fetched = await repo.get(created.id)

    assert fetched is not None
    assert fetched.provider_name == "Dr. Smith"
    assert fetched.is_booked is False


@pytest.mark.asyncio
async def test_availability_find_open_slots_filters_booked(session: AsyncSession) -> None:
    repo = AvailabilityRepository(session)
    window_start = _dt(0)
    window_end = _dt(240)

    open_slot = await repo.create(
        provider_name="Dr. Open",
        start_ts=_dt(30),
        end_ts=_dt(60),
    )
    booked_slot = await repo.create(
        provider_name="Dr. Booked",
        start_ts=_dt(45),
        end_ts=_dt(75),
        is_booked=True,
    )
    outside_window_slot = await repo.create(
        provider_name="Dr. Later",
        start_ts=_dt(300),
        end_ts=_dt(330),
    )

    open_slots = await repo.find_open_slots(window_start, window_end)

    open_ids = {slot.id for slot in open_slots}
    assert open_slot.id in open_ids
    assert booked_slot.id not in open_ids
    assert outside_window_slot.id not in open_ids


@pytest.mark.asyncio
async def test_availability_mark_booked(session: AsyncSession) -> None:
    repo = AvailabilityRepository(session)
    slot = await repo.create(provider_name="Dr. Who", start_ts=_dt(10), end_ts=_dt(40))

    updated = await repo.mark_booked(slot)

    assert updated.is_booked is True
    fetched = await repo.get(slot.id)
    assert fetched is not None
    assert fetched.is_booked is True


# --- Appointment ---------------------------------------------------------


@pytest.mark.asyncio
async def test_appointment_create_and_get_roundtrip(session: AsyncSession) -> None:
    patient = await PatientRepository(session).create(
        full_name="Rosalind Franklin", phone="+15551110000"
    )
    availability = await AvailabilityRepository(session).create(
        provider_name="Dr. X", start_ts=_dt(10), end_ts=_dt(40)
    )
    repo = AppointmentRepository(session)

    created = await repo.create(
        patient_id=patient.id,
        availability_id=availability.id,
        reason="Checkup",
    )

    fetched = await repo.get(created.id)
    assert fetched is not None
    assert fetched.status == AppointmentStatus.scheduled
    assert fetched.patient_id == patient.id


@pytest.mark.asyncio
async def test_appointment_one_per_availability_unique_constraint(
    session: AsyncSession,
) -> None:
    patient_repo = PatientRepository(session)
    availability_repo = AvailabilityRepository(session)
    repo = AppointmentRepository(session)

    patient_a = await patient_repo.create(full_name="Patient A", phone="+15552220000")
    patient_b = await patient_repo.create(full_name="Patient B", phone="+15552220001")
    availability = await availability_repo.create(
        provider_name="Dr. Shared", start_ts=_dt(10), end_ts=_dt(40)
    )

    await repo.create(patient_id=patient_a.id, availability_id=availability.id)

    with pytest.raises(IntegrityError):
        await repo.create(patient_id=patient_b.id, availability_id=availability.id)

    await session.rollback()


@pytest.mark.asyncio
async def test_appointment_list_by_patient_and_status(session: AsyncSession) -> None:
    patient = await PatientRepository(session).create(
        full_name="Marie Curie", phone="+15553330000"
    )
    availability_repo = AvailabilityRepository(session)
    repo = AppointmentRepository(session)

    slot_one = await availability_repo.create(
        provider_name="Dr. One", start_ts=_dt(10), end_ts=_dt(40)
    )
    slot_two = await availability_repo.create(
        provider_name="Dr. Two", start_ts=_dt(50), end_ts=_dt(80)
    )

    appt_one = await repo.create(patient_id=patient.id, availability_id=slot_one.id)
    appt_two = await repo.create(
        patient_id=patient.id,
        availability_id=slot_two.id,
        status=AppointmentStatus.confirmed,
    )

    by_patient = await repo.list_by_patient(patient.id)
    scheduled = await repo.list_by_status(AppointmentStatus.scheduled)
    confirmed = await repo.list_by_status(AppointmentStatus.confirmed)

    assert {a.id for a in by_patient} == {appt_one.id, appt_two.id}
    assert {a.id for a in scheduled} == {appt_one.id}
    assert {a.id for a in confirmed} == {appt_two.id}


# --- Callback --------------------------------------------------------------


@pytest.mark.asyncio
async def test_callback_create_and_get_roundtrip(session: AsyncSession) -> None:
    repo = CallbackRepository(session)
    created = await repo.create(priority=CallbackPriority.normal, reason="Reschedule")

    fetched = await repo.get(created.id)

    assert fetched is not None
    assert fetched.status == CallbackStatus.pending
    assert fetched.reason == "Reschedule"


@pytest.mark.asyncio
async def test_callback_queue_ordering_and_emergencies(session: AsyncSession) -> None:
    repo = CallbackRepository(session)

    normal_cb = await repo.create(priority=CallbackPriority.normal, reason="Question")
    urgent_cb = await repo.create(priority=CallbackPriority.urgent, reason="Pain")
    emergency_cb = await repo.create(
        priority=CallbackPriority.emergency, reason="Chest pain"
    )
    # Already resolved; must never appear in the queue.
    resolved_cb = await repo.create(
        priority=CallbackPriority.emergency,
        reason="Resolved emergency",
        status=CallbackStatus.resolved,
    )

    queued = await repo.queue()
    emergencies = await repo.list_pending_emergencies()

    queued_ids = [cb.id for cb in queued]
    assert queued_ids == [emergency_cb.id, urgent_cb.id, normal_cb.id]
    assert resolved_cb.id not in queued_ids
    assert [cb.id for cb in emergencies] == [emergency_cb.id]


# --- CallLog / Conversation --------------------------------------------------


@pytest.mark.asyncio
async def test_call_log_create_and_get_by_room(session: AsyncSession) -> None:
    repo = CallLogRepository(session)
    created = await repo.create(room_name="room-123", outcome=CallOutcome.completed)

    fetched = await repo.get_by_room("room-123")

    assert fetched is not None
    assert fetched.id == created.id
    assert await repo.get_by_room("missing-room") is None


@pytest.mark.asyncio
async def test_conversation_add_message_and_list_for_call(session: AsyncSession) -> None:
    call_log = await CallLogRepository(session).create(room_name="room-456")
    repo = ConversationRepository(session)

    await repo.add_message(call_log.id, ConversationRole.patient, "Hello")
    await repo.add_message(call_log.id, ConversationRole.assistant, "Hi, how can I help?")

    messages = await repo.list_for_call(call_log.id)

    assert [m.role for m in messages] == [
        ConversationRole.patient,
        ConversationRole.assistant,
    ]
    assert [m.content for m in messages] == ["Hello", "Hi, how can I help?"]


@pytest.mark.asyncio
async def test_conversation_cascade_delete_when_call_log_deleted(
    session: AsyncSession,
) -> None:
    call_log_repo = CallLogRepository(session)
    conversation_repo = ConversationRepository(session)

    call_log = await call_log_repo.create(room_name="room-789")
    await conversation_repo.add_message(call_log.id, ConversationRole.patient, "Hi")
    await conversation_repo.add_message(call_log.id, ConversationRole.assistant, "Hello")

    remaining = await conversation_repo.list_for_call(call_log.id)
    assert len(remaining) == 2

    await call_log_repo.delete(call_log)

    remaining_after_delete = await conversation_repo.list_for_call(call_log.id)
    assert remaining_after_delete == []


# --- Audit -------------------------------------------------------------------


@pytest.mark.asyncio
async def test_audit_record(session: AsyncSession) -> None:
    repo = AuditRepository(session)

    entry = await repo.record(
        actor="system",
        action="patient.create",
        entity="Patient",
        entity_id=42,
        meta={"source": "voice_call"},
    )

    fetched = await repo.get(entry.id)
    assert fetched is not None
    assert fetched.actor == "system"
    assert fetched.meta == {"source": "voice_call"}


# --- get_or_404 --------------------------------------------------------------


@pytest.mark.asyncio
async def test_get_or_404_raises_not_found(session: AsyncSession) -> None:
    repo = PatientRepository(session)

    with pytest.raises(NotFoundError):
        await repo.get_or_404(999_999)
