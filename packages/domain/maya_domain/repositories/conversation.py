"""Repository for :class:`ConversationHistory` transcript turns."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import select

from maya_domain.models.conversation import ConversationHistory
from maya_domain.models.enums import ConversationRole
from maya_domain.repositories.base import BaseRepository


class ConversationRepository(BaseRepository[ConversationHistory]):
    """Data access for call transcript turns."""

    model = ConversationHistory

    async def add_message(
        self, call_log_id: int, role: ConversationRole, content: str
    ) -> ConversationHistory:
        """Append a transcript turn to a call and flush."""
        return await self.create(call_log_id=call_log_id, role=role, content=content)

    async def list_for_call(self, call_log_id: int) -> Sequence[ConversationHistory]:
        """Return all transcript turns for a call, oldest first."""
        stmt = (
            select(ConversationHistory)
            .where(ConversationHistory.call_log_id == call_log_id)
            .order_by(ConversationHistory.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
