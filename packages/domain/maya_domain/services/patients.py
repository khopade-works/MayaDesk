"""Shared patient resolution used by booking and callback use cases."""

from __future__ import annotations

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.models.patient import Patient
from maya_domain.repositories.patient import PatientRepository


async def get_or_create_patient(
    session: AsyncSession, *, full_name: str, phone: str
) -> Patient:
    """Return the patient with ``phone``, creating one if none exists.

    Existing patients are matched by phone (the natural key) and returned as-is;
    the name is not overwritten. A concurrent insert on the unique phone is
    resolved by re-reading the winning row.
    """
    repo = PatientRepository(session)
    existing = await repo.get_by_phone(phone)
    if existing is not None:
        return existing

    try:
        # SAVEPOINT so a concurrent insert on the unique phone rolls back only
        # this nested scope, never the caller's outer transaction.
        async with session.begin_nested():
            return await repo.create(full_name=full_name, phone=phone)
    except IntegrityError:
        winner = await repo.get_by_phone(phone)
        if winner is None:  # pragma: no cover - only if the row vanished mid-race
            raise
        return winner
