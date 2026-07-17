"""Read queries powering the staff dashboard.

Pure reads: no mutation, no unit of work required. Joins are eager-loaded so each
list renders from a single round trip.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from maya_domain.models.appointment import Appointment
from maya_domain.models.availability import Availability
from maya_domain.models.callback import Callback
from maya_domain.models.enums import (
    AppointmentStatus,
    CallbackPriority,
    CallbackStatus,
)
from maya_domain.repositories.callback import _PRIORITY_RANK
from maya_domain.schemas.views import AppointmentView, CallbackView, DashboardStats


async def list_appointments(
    session: AsyncSession,
    *,
    status: AppointmentStatus | None = None,
    search: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[AppointmentView]:
    """List appointments (joined to patient + slot), newest slot first.

    ``search`` matches the patient's name or phone (case-insensitive substring).
    """
    stmt = (
        select(Appointment)
        .join(Appointment.availability)
        .join(Appointment.patient)
        .options(
            selectinload(Appointment.patient),
            selectinload(Appointment.availability),
        )
        .order_by(Availability.start_ts.desc())
        .limit(limit)
        .offset(offset)
    )
    if status is not None:
        stmt = stmt.where(Appointment.status == status)
    if search:
        from maya_domain.models.patient import Patient

        needle = f"%{_escape_like(search.strip().lower())}%"
        stmt = stmt.where(
            or_(
                func.lower(Patient.full_name).like(needle, escape="\\"),
                func.lower(Patient.phone).like(needle, escape="\\"),
            )
        )

    rows = (await session.execute(stmt)).scalars().all()
    return [
        AppointmentView(
            id=a.id,
            patient_name=a.patient.full_name,
            patient_phone=a.patient.phone,
            provider_name=a.availability.provider_name,
            start_ts=a.availability.start_ts,
            end_ts=a.availability.end_ts,
            status=a.status,
            reason=a.reason,
            created_at=a.created_at,
        )
        for a in rows
    ]


async def list_callbacks(
    session: AsyncSession,
    *,
    status: CallbackStatus | None = CallbackStatus.pending,
) -> list[CallbackView]:
    """List callbacks ordered by priority (emergency first), then age."""
    stmt = (
        select(Callback)
        .options(selectinload(Callback.patient))
        .order_by(_PRIORITY_RANK.desc(), Callback.created_at)
    )
    if status is not None:
        stmt = stmt.where(Callback.status == status)

    rows = (await session.execute(stmt)).scalars().all()
    return [_to_callback_view(c) for c in rows]


async def list_emergencies(session: AsyncSession) -> list[CallbackView]:
    """List pending emergency callbacks, oldest first."""
    stmt = (
        select(Callback)
        .options(selectinload(Callback.patient))
        .where(
            Callback.status == CallbackStatus.pending,
            Callback.priority == CallbackPriority.emergency,
        )
        .order_by(Callback.created_at)
    )
    rows = (await session.execute(stmt)).scalars().all()
    return [_to_callback_view(c) for c in rows]


async def get_stats(session: AsyncSession) -> DashboardStats:
    """Return headline counts for the dashboard."""
    now = datetime.now(timezone.utc)

    appts_total = await _scalar(session, select(func.count()).select_from(Appointment))
    upcoming = await _scalar(
        session,
        select(func.count())
        .select_from(Appointment)
        .join(Appointment.availability)
        .where(
            Availability.start_ts >= now,
            Appointment.status.in_(
                [AppointmentStatus.scheduled, AppointmentStatus.confirmed]
            ),
        ),
    )
    callbacks_pending = await _scalar(
        session,
        select(func.count())
        .select_from(Callback)
        .where(Callback.status == CallbackStatus.pending),
    )
    emergencies = await _scalar(
        session,
        select(func.count())
        .select_from(Callback)
        .where(
            Callback.status == CallbackStatus.pending,
            Callback.priority == CallbackPriority.emergency,
        ),
    )
    return DashboardStats(
        appointments_total=appts_total,
        appointments_upcoming=upcoming,
        callbacks_pending=callbacks_pending,
        emergencies_pending=emergencies,
    )


def _to_callback_view(c: Callback) -> CallbackView:
    return CallbackView(
        id=c.id,
        patient_name=c.patient.full_name if c.patient else None,
        patient_phone=c.patient.phone if c.patient else None,
        priority=c.priority,
        reason=c.reason,
        status=c.status,
        created_at=c.created_at,
    )


async def _scalar(session: AsyncSession, stmt) -> int:
    return (await session.execute(stmt)).scalar_one()


def _escape_like(term: str) -> str:
    """Escape LIKE metacharacters so user search input is treated literally."""
    return term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
