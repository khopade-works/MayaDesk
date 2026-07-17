"""Request/call correlation identifiers backed by :mod:`contextvars`.

A single request (or voice call) is tagged with a ``request_id`` that flows
through logs and error responses without threading it manually through every
call site.
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar

import structlog

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)


def bind_request_id(request_id: str | None = None) -> str:
    """Bind a request id to the current context and structlog context.

    Generates a UUID4 when ``request_id`` is not supplied. Returns the value
    that was bound so callers can echo it back (e.g. via an ``X-Request-ID``
    response header).
    """
    resolved = request_id or uuid.uuid4().hex
    request_id_var.set(resolved)
    structlog.contextvars.bind_contextvars(request_id=resolved)
    return resolved


def get_request_id() -> str | None:
    """Return the request id bound to the current context, if any."""
    return request_id_var.get()


def clear_request_id() -> None:
    """Reset the request id in both the contextvar and structlog context."""
    request_id_var.set(None)
    structlog.contextvars.unbind_contextvars("request_id")
