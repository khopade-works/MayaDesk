"""``check_availability`` tool — offer open appointment slots to the caller."""

from __future__ import annotations

from typing import Any

from livekit.agents import RunContext, function_tool

from maya_domain.database import unit_of_work
from maya_domain.services import list_open_slots

from maya_agent.tools.formatting import format_when
from maya_agent.tools.guards import ToolTimeoutError, run_guarded


async def check_availability_impl() -> dict[str, Any]:
    """Return open slots as plain data (unit-testable, no LiveKit context)."""

    async def _load() -> list:
        async with unit_of_work() as session:
            return list(await list_open_slots(session))

    try:
        slots = await run_guarded(_load, label="check_availability")
    except ToolTimeoutError:
        return {"count": 0, "slots": [], "error": "timeout"}

    return {
        "count": len(slots),
        "slots": [
            {
                "slot_id": slot.id,
                "when": format_when(slot.start_ts),
                "provider": slot.provider_name,
            }
            for slot in slots
        ],
    }


@function_tool()
async def check_availability(context: RunContext) -> dict[str, Any]:
    """List open appointment slots the patient can book.

    Each slot includes a ``slot_id`` (required to book), a spoken-friendly time,
    and the provider's name. Offer the caller one or two options at a time.
    """
    return await check_availability_impl()
