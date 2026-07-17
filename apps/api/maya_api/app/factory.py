"""FastAPI application factory.

Assembles the app from its parts: logging + engine lifespan, CORS, the
``AppError`` -> JSON exception handler, request-context middleware, and routers.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from maya_domain.config import get_settings
from maya_domain.core.context import get_request_id
from maya_domain.core.errors import AppError
from maya_domain.core.logging import configure_logging, get_logger
from maya_domain.database.engine import get_engine

from maya_api.api.dashboard import router as dashboard_router
from maya_api.api.health import router as health_router
from maya_api.api.internal import router as internal_router
from maya_api.api.tokens import router as tokens_router
from maya_api.app.middleware import RequestContextMiddleware
from maya_api.app.rate_limit import limiter
from maya_api.app.security import SecurityHeadersMiddleware
from maya_api.websocket import dashboard_ws_router


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Configure logging on startup and dispose the engine on shutdown."""
    settings = get_settings()
    configure_logging(level=settings.log_level, env=settings.env)
    logger = get_logger("maya_api.lifespan")
    logger.info("startup", env=settings.env)
    try:
        yield
    finally:
        await get_engine().dispose()
        logger.info("shutdown")


async def _app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    """Translate a domain :class:`AppError` into a JSON response."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.__class__.__name__,
            "detail": exc.message,
            "request_id": get_request_id(),
        },
    )


async def _rate_limit_exceeded_handler(
    _request: Request, exc: RateLimitExceeded
) -> JSONResponse:
    """Translate a slowapi :class:`RateLimitExceeded` into a JSON 429 response."""
    return JSONResponse(
        status_code=429,
        content={
            "error": "RateLimitExceeded",
            "detail": str(exc.detail) if exc.detail else "Rate limit exceeded.",
            "request_id": get_request_id(),
        },
    )


async def _unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Log an unexpected exception and return a generic 500 without leaking internals.

    This handler is invoked by Starlette's outermost ``ServerErrorMiddleware``,
    above :class:`RequestContextMiddleware`, whose ``finally`` block has
    already cleared the request-id contextvar by the time we get here — so the
    id is read from ``request.state`` (set on the shared ASGI scope) instead.
    """
    request_id = get_request_id() or getattr(request.state, "request_id", None)
    get_logger("maya_api.unhandled").exception(
        "request.unhandled_exception", exc_type=exc.__class__.__name__, request_id=request_id
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "InternalServerError",
            "detail": "An unexpected error occurred.",
            "request_id": request_id,
        },
    )


def create_app() -> FastAPI:
    """Build and return the configured FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="MayaDesk API",
        version="0.1.0",
        description="AI healthcare voice receptionist — HTTP API.",
        lifespan=_lifespan,
    )

    app.state.limiter = limiter

    # Middleware executes outside-in on the request path; the last one added
    # here (SecurityHeadersMiddleware) wraps the whole stack.
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins or [],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestContextMiddleware)
    app.add_middleware(SecurityHeadersMiddleware, is_production=settings.is_production)

    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]
    app.add_exception_handler(AppError, _app_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, _unhandled_exception_handler)

    app.include_router(health_router)
    app.include_router(tokens_router)
    app.include_router(dashboard_router)
    app.include_router(internal_router)
    app.include_router(dashboard_ws_router)

    return app
