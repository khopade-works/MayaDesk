"""Repository for the append-only :class:`AuditLog` trail."""

from __future__ import annotations

from typing import Any

from maya_domain.models.audit import AuditLog
from maya_domain.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditLog]):
    """Data access for audit log entries."""

    model = AuditLog

    async def record(
        self,
        actor: str,
        action: str,
        entity: str,
        entity_id: int | None = None,
        meta: dict[str, Any] | None = None,
    ) -> AuditLog:
        """Append an audit entry and flush."""
        return await self.create(
            actor=actor,
            action=action,
            entity=entity,
            entity_id=entity_id,
            meta=meta,
        )
