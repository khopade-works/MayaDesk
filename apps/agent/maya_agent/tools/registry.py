"""The function-tool registry handed to the Maya agent."""

from __future__ import annotations

from maya_agent.tools.availability import check_availability
from maya_agent.tools.booking import book_appointment
from maya_agent.tools.callback import flag_for_human_callback

# Order is cosmetic; the LLM selects tools by name and description.
TOOLS = [check_availability, book_appointment, flag_for_human_callback]
