"""The Maya agent definition.

Maya's identity and guardrails live in :mod:`maya_agent.prompts`. Function tools
(check availability, book appointment, flag callback) are added in Phase 4.
"""

from __future__ import annotations

from livekit.agents import Agent

from maya_agent.prompts import SYSTEM_PROMPT
from maya_agent.tools import TOOLS


class MayaAgent(Agent):
    """Maya — the healthcare receptionist agent.

    Carries Maya's instructions and the booking/availability/callback function
    tools, which execute real backend actions against the database.
    """

    def __init__(self) -> None:
        super().__init__(instructions=SYSTEM_PROMPT, tools=TOOLS)
