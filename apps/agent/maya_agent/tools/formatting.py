"""Presentation helpers for tool results spoken back to the caller."""

from __future__ import annotations

from datetime import datetime


def format_when(dt: datetime) -> str:
    """Render a slot time as a natural phrase, e.g. 'Tuesday, July 22 at 02:30 PM'."""
    return dt.strftime("%A, %B %d at %I:%M %p")
