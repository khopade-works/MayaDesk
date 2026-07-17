"""Repository for :class:`CallLog` aggregates."""

from __future__ import annotations

from sqlalchemy import select

from maya_domain.models.call_log import CallLog
from maya_domain.repositories.base import BaseRepository


class CallLogRepository(BaseRepository[CallLog]):
    """Data access for voice call records."""

    model = CallLog

    async def get_by_room(self, room_name: str) -> CallLog | None:
        """Return the call log for the given LiveKit room name, or ``None``."""
        stmt = select(CallLog).where(CallLog.room_name == room_name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
