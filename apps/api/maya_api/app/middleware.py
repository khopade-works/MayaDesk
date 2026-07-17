"""HTTP middleware: request-id correlation, timing, and structured logging."""

from __future__ import annotations

import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from maya_domain.core.context import bind_request_id, clear_request_id
from maya_domain.core.logging import get_logger

_REQUEST_ID_HEADER = "X-Request-ID"

_logger = get_logger("maya_api.request")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Bind a request id, time each request, and emit structured start/end logs.

    An inbound ``X-Request-ID`` header is honoured when present; otherwise a new
    id is generated. The resolved id is echoed on the response.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        incoming = request.headers.get(_REQUEST_ID_HEADER)
        request_id = bind_request_id(incoming)
        # Also stash on request.state: it survives on the shared ASGI scope even
        # after the `finally` below clears the contextvar, so outermost handlers
        # (e.g. the catch-all 500 handler, which runs above this middleware) can
        # still recover the id for an exception that unwinds past `call_next`.
        request.state.request_id = request_id

        _logger.info(
            "request.start",
            method=request.method,
            path=request.url.path,
        )
        start = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            _logger.exception(
                "request.error",
                method=request.method,
                path=request.url.path,
                elapsed_ms=round(elapsed_ms, 3),
            )
            raise
        else:
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            response.headers[_REQUEST_ID_HEADER] = request_id
            _logger.info(
                "request.end",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                elapsed_ms=round(elapsed_ms, 3),
            )
            return response
        finally:
            clear_request_id()
