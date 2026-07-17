"""Read endpoints powering the staff dashboard.

All routes are pure reads over the shared database, so they reflect writes from
both the API and the voice agent. The frontend polls these on an interval for
near-real-time updates (WebSocket + Redis pub/sub is the production upgrade).
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from maya_domain.database.session import get_session
from maya_domain.models.enums import AppointmentStatus, CallbackStatus
from maya_domain.schemas.views import AppointmentView, CallbackView, DashboardStats
from maya_domain.services import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.get("/stats", response_model=DashboardStats)
async def stats(session: SessionDep) -> DashboardStats:
    """Headline counts for the dashboard header."""
    return await dashboard_service.get_stats(session)


@router.get("/appointments", response_model=list[AppointmentView])
async def appointments(
    session: SessionDep,
    status: AppointmentStatus | None = None,
    search: Annotated[str | None, Query(max_length=128)] = None,
    limit: Annotated[int, Query(ge=1, le=200)] = 100,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AppointmentView]:
    """List appointments, optionally filtered by status and patient search."""
    return await dashboard_service.list_appointments(
        session, status=status, search=search, limit=limit, offset=offset
    )


@router.get("/callbacks", response_model=list[CallbackView])
async def callbacks(
    session: SessionDep,
    status: CallbackStatus | None = CallbackStatus.pending,
) -> list[CallbackView]:
    """List callbacks ordered by priority, defaulting to the pending queue."""
    return await dashboard_service.list_callbacks(session, status=status)


@router.get("/emergencies", response_model=list[CallbackView])
async def emergencies(session: SessionDep) -> list[CallbackView]:
    """List pending emergency callbacks for the alert banner."""
    return await dashboard_service.list_emergencies(session)
