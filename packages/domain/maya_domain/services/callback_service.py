"""Callback use case: log a human callback request (including emergencies).

Emergencies come in here as ``CallbackPriority.emergency`` so the staff
dashboard's emergency queue and the ordinary callback queue read from one place.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.models.enums import CallbackPriority, CallbackStatus
from maya_domain.repositories.audit import AuditRepository
from maya_domain.repositories.callback import CallbackRepository
from maya_domain.services.patients import get_or_create_patient
from maya_domain.services.results import CallbackResult

_ACTOR = "agent:maya"


async def request_callback(
    session: AsyncSession,
    *,
    patient_name: str,
    patient_phone: str,
    reason: str,
    priority: CallbackPriority | str = CallbackPriority.urgent,
) -> CallbackResult:
    """Create a pending callback for the patient at the given priority."""
    priority = CallbackPriority(priority)

    patient = await get_or_create_patient(
        session, full_name=patient_name, phone=patient_phone
    )

    callbacks = CallbackRepository(session)
    audit = AuditRepository(session)

    callback = await callbacks.create(
        patient_id=patient.id,
        reason=reason,
        priority=priority,
        status=CallbackStatus.pending,
    )
    await audit.record(
        actor=_ACTOR,
        action="flag_for_human_callback",
        entity="callback",
        entity_id=callback.id,
        meta={"patient_id": patient.id, "priority": priority.value},
    )

    return CallbackResult(
        callback_id=callback.id,
        priority=priority.value,
        status=callback.status.value,
    )
