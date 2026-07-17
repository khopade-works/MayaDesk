"""``book_appointment`` tool — reserve a chosen slot for the caller."""

from __future__ import annotations

from typing import Any

from livekit.agents import RunContext, function_tool

from maya_domain.core.errors import ConflictError, NotFoundError
from maya_domain.database import unit_of_work
from maya_domain.services import book_appointment as _book_appointment
from maya_domain.services.results import BookingResult

from maya_agent.events import emit_dashboard_event
from maya_agent.tools.formatting import format_when
from maya_agent.tools.guards import ToolTimeoutError, run_guarded


async def book_appointment_impl(
    *,
    patient_name: str,
    patient_phone: str,
    slot_id: int,
    reason: str | None = None,
) -> dict[str, Any]:
    """Book a slot, returning a result dict. Conflicts are returned, not raised."""

    async def _book() -> BookingResult:
        async with unit_of_work() as session:
            return await _book_appointment(
                session,
                patient_name=patient_name,
                patient_phone=patient_phone,
                availability_id=slot_id,
                reason=reason,
            )

    try:
        result = await run_guarded(_book, label="book_appointment")
    except (ConflictError, NotFoundError) as exc:
        return {"ok": False, "message": str(exc)}
    except ToolTimeoutError:
        return {"ok": False, "message": "The booking system is slow right now; please try again."}

    emit_dashboard_event(
        "appointment_booked",
        {
            "appointment_id": result.appointment_id,
            "patient_name": result.patient_name,
            "provider_name": result.provider_name,
        },
    )

    return {
        "ok": True,
        "appointment_id": result.appointment_id,
        "patient": result.patient_name,
        "provider": result.provider_name,
        "when": format_when(result.start_ts),
    }


@function_tool()
async def book_appointment(
    context: RunContext,
    patient_name: str,
    patient_phone: str,
    slot_id: int,
    reason: str | None = None,
) -> dict[str, Any]:
    """Book an appointment slot for a patient.

    Confirm the patient's full name and phone number, and the ``slot_id`` from
    check_availability, before calling. If ``ok`` is false, the slot was taken —
    offer another time.

    Args:
        patient_name: The patient's full name.
        patient_phone: The patient's phone number.
        slot_id: The slot_id returned by check_availability.
        reason: Optional brief reason for the visit.
    """
    return await book_appointment_impl(
        patient_name=patient_name,
        patient_phone=patient_phone,
        slot_id=slot_id,
        reason=reason,
    )
