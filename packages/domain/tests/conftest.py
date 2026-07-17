"""Shared pytest-asyncio fixtures: a fresh in-memory SQLite schema per test."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import StaticPool

import maya_domain.models  # noqa: F401  (registers all models on Base.metadata)
from maya_domain.database.base import Base


def _enable_sqlite_foreign_keys(dbapi_connection: object, _record: object) -> None:
    """Turn on SQLite foreign-key enforcement for every new connection."""
    cursor = dbapi_connection.cursor()  # type: ignore[attr-defined]
    try:
        cursor.execute("PRAGMA foreign_keys=ON;")
    finally:
        cursor.close()


@pytest_asyncio.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    """A fresh in-memory SQLite async engine with the full schema, per test."""
    test_engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    sync_engine: Engine = test_engine.sync_engine
    event.listen(sync_engine, "connect", _enable_sqlite_foreign_keys)

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield test_engine
    finally:
        await test_engine.dispose()


@pytest_asyncio.fixture
async def session(engine: AsyncEngine) -> AsyncIterator[AsyncSession]:
    """An :class:`AsyncSession` bound to the per-test engine."""
    session_factory = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with session_factory() as db_session:
        yield db_session
