"""Unit-of-work: the transaction boundary for use cases.

Repositories flush but never commit. A use case runs inside ``unit_of_work``,
which yields a session, commits once on success, and rolls back on any error.
This is what makes a booking atomic: creating the appointment, flipping the slot
to booked, and writing the audit entry either all land together or not at all.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.database.session import AsyncSessionLocal


@asynccontextmanager
async def unit_of_work() -> AsyncIterator[AsyncSession]:
    """Yield a session that commits on success and rolls back on failure."""
    session = AsyncSessionLocal()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
