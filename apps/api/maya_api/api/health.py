"""Service banner and health endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from maya_domain.config import get_settings
from maya_domain.core.logging import get_logger
from maya_domain.database.session import ping

router = APIRouter(tags=["system"])

_logger = get_logger("maya_api.health")


@router.get("/")
async def root() -> dict[str, str]:
    """Return a basic service banner."""
    return {
        "service": "maya-api",
        "name": "MayaDesk",
        "status": "running",
    }


@router.get("/health")
async def health() -> JSONResponse:
    """Report liveness plus a live database connectivity check.

    Returns HTTP 200 when the database responds and 503 when it does not.
    """
    settings = get_settings()
    try:
        db_up = await ping()
    except Exception:
        _logger.exception("health.db_ping_failed")
        db_up = False

    payload = {
        "status": "ok" if db_up else "degraded",
        "env": settings.env,
        "db": "up" if db_up else "down",
    }
    return JSONResponse(
        status_code=200 if db_up else 503,
        content=payload,
    )
