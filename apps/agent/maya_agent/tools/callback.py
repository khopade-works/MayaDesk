"""``flag_for_human_callback`` tool — escalate to a human, including emergencies."""

from __future__ import annotations

from typing import Any

from livekit.agents import RunContext, function_tool

from maya_domain.database import unit_of_work
from maya_domain.models.enums import CallbackPriority
from maya_domain.services import request_callback
from maya_domain.services.results import CallbackResult

from maya_agent.events import emit_dashboard_event
from maya_agent.tools.guards import ToolTimeoutError, run_guarded

_VALID_PRIORITIES = {p.value for p in CallbackPriority}


async def flag_for_human_callback_impl(
    *,
    patient_name: str,
    patient_phone: str,
    reason: str,
    priority: str = "urgent",
) -> dict[str, Any]:
    """Log a callback request, returning a result dict."""
    normalized = priority if priority in _VALID_PRIORITIES else CallbackPriority.urgent.value

    async def _request() -> CallbackResult:
        async with unit_of_work() as session:
            return await request_callback(
                session,
                patient_name=patient_name,
                patient_phone=patient_phone,
                reason=reason,
                priority=normalized,
            )

    try:
        result = await run_guarded(_request, label="flag_for_human_callback")
    except ToolTimeoutError:
        return {"ok": False, "message": "Could not log the callback in time; please try again."}

    emit_dashboard_event(
        "emergency" if result.priority == CallbackPriority.emergency.value else "callback_created",
        {"callback_id": result.callback_id, "priority": result.priority},
    )

    return {
        "ok": True,
        "callback_id": result.callback_id,
        "priority": result.priority,
        "status": result.status,
    }


@function_tool()
async def flag_for_human_callback(
    context: RunContext,
    patient_name: str,
    patient_phone: str,
    reason: str,
    priority: str = "urgent",
) -> dict[str, Any]:
    """Log a request for a human staff member to call the patient back.

    Use ``priority="emergency"`` for life-threatening situations (chest pain,
    severe bleeding, stroke, suicidal thoughts, loss of consciousness, difficulty
    breathing) after advising the caller to contact emergency services.

    Args:
        patient_name: The patient's full name.
        patient_phone: The patient's phone number.
        reason: Brief reason the callback is needed.
        priority: One of "normal", "urgent", or "emergency".
    """
    return await flag_for_human_callback_impl(
        patient_name=patient_name,
        patient_phone=patient_phone,
        reason=reason,
        priority=priority,
    )
