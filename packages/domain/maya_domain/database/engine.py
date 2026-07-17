"""Async SQLAlchemy engine construction.

Builds a single process-wide :class:`AsyncEngine` from settings. For SQLite the
engine installs a connection listener that enables WAL journaling and enforces
foreign-key constraints on every new connection.
"""

from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from maya_domain.config import get_settings


def _apply_sqlite_pragmas(dbapi_connection: object, _record: object) -> None:
    """Enable WAL journaling and foreign-key enforcement for SQLite."""
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    try:
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA foreign_keys=ON;")
    finally:
        cursor.close()


def _build_engine() -> AsyncEngine:
    settings = get_settings()
    url = settings.database_url
    is_sqlite = url.startswith("sqlite")

    new_engine = create_async_engine(
        url,
        echo=False,
        future=True,
        pool_pre_ping=True,
    )

    if is_sqlite:
        # The listener attaches to the underlying sync engine of the async engine.
        sync_engine: Engine = new_engine.sync_engine
        event.listen(sync_engine, "connect", _apply_sqlite_pragmas)

    return new_engine


# Process-wide engine instance.
engine: AsyncEngine = _build_engine()


def get_engine() -> AsyncEngine:
    """Return the shared async engine."""
    return engine
