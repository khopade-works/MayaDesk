"""Booking use case: atomically reserve a slot for a patient.

The whole operation runs inside the caller's unit of work: resolve the patient,
verify the slot is free, create the appointment, flip the slot to booked, and
write an audit entry. Any failure rolls the entire transaction back, so a slot
can never be left half-booked.
"""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.core.errors import ConflictError
from maya_domain.models.enums import AppointmentStatus
from maya_domain.repositories.appointment import AppointmentRepository
from maya_domain.repositories.audit import AuditRepository
from maya_domain.repositories.availability import AvailabilityRepository
from maya_domain.services.patients import get_or_create_patient
from maya_domain.services.results import BookingResult

_ACTOR = "agent:maya"


async def book_appointment(
    session: AsyncSession,
    *,
    patient_name: str,
    patient_phone: str,
    availability_id: int,
    reason: str | None = None,
) -> BookingResult:
    """Book ``availability_id`` for the given patient.

    :raises NotFoundError: the slot does not exist.
    :raises ConflictError: the slot is already booked.
    """
    slots = AvailabilityRepository(session)
    appointments = AppointmentRepository(session)
    audit = AuditRepository(session)

    slot = await slots.get_or_404(availability_id)
    if slot.is_booked:
        raise ConflictError("That appointment time is no longer available.")

    patient = await get_or_create_patient(
        session, full_name=patient_name, phone=patient_phone
    )

    try:
        # SAVEPOINT: if the unique constraint on availability_id trips a
        # concurrent booking, only this nested scope rolls back — the caller's
        # transaction stays usable, so raising ConflictError never leaves a
        # poisoned session behind.
        async with session.begin_nested():
            appointment = await appointments.create(
                patient_id=patient.id,
                availability_id=slot.id,
                reason=reason,
                status=AppointmentStatus.scheduled,
            )
    except IntegrityError as exc:
        raise ConflictError("That appointment time was just taken.") from exc

    await slots.mark_booked(slot)
    await audit.record(
        actor=_ACTOR,
        action="book_appointment",
        entity="appointment",
        entity_id=appointment.id,
        meta={"patient_id": patient.id, "availability_id": slot.id},
    )

    return BookingResult(
        appointment_id=appointment.id,
        patient_name=patient.full_name,
        provider_name=slot.provider_name,
        start_ts=slot.start_ts,
        status=appointment.status.value,
    )
