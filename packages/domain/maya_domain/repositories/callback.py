"""Repository for :class:`Callback` aggregates."""

from __future__ import annotations

from collections.abc import Sequence

from sqlalchemy import case, select

from maya_domain.models.callback import Callback
from maya_domain.models.enums import CallbackPriority, CallbackStatus
from maya_domain.repositories.base import BaseRepository

# Higher rank sorts first: emergencies ahead of urgent ahead of normal.
_PRIORITY_RANK = case(
    (Callback.priority == CallbackPriority.emergency, 2),
    (Callback.priority == CallbackPriority.urgent, 1),
    else_=0,
)


class CallbackRepository(BaseRepository[Callback]):
    """Data access for callback requests awaiting a call back."""

    model = Callback

    async def queue(self) -> Sequence[Callback]:
        """Return pending callbacks ordered by priority (desc), then age (oldest first)."""
        stmt = (
            select(Callback)
            .where(Callback.status == CallbackStatus.pending)
            .order_by(_PRIORITY_RANK.desc(), Callback.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def list_pending_emergencies(self) -> Sequence[Callback]:
        """Return pending emergency callbacks, oldest first."""
        stmt = (
            select(Callback)
            .where(
                Callback.status == CallbackStatus.pending,
                Callback.priority == CallbackPriority.emergency,
            )
            .order_by(Callback.created_at)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
