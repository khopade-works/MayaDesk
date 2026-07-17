"""Cancellation guard for tool database work.

A tool must never block the live call. Each database action runs under a
timeout; if it overruns, the awaited work is cancelled (rolling back its unit of
work) and the tool reports failure so Maya can move the conversation forward.
"""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

from maya_domain.core.logging import get_logger

from maya_agent.config import get_voice_config

_T = TypeVar("_T")
_logger = get_logger("maya_agent.tools")


class ToolTimeoutError(Exception):
    """Raised when a tool's database work exceeds its deadline."""


async def run_guarded(factory: Callable[[], Awaitable[_T]], *, label: str) -> _T:
    """Run ``factory()`` under the configured tool timeout.

    :raises ToolTimeoutError: if the work does not complete in time.
    """
    timeout = get_voice_config().tool_timeout_seconds
    try:
        return await asyncio.wait_for(factory(), timeout=timeout)
    except asyncio.TimeoutError as exc:
        _logger.warning("tool.timeout", tool=label, timeout_s=timeout)
        raise ToolTimeoutError(label) from exc
