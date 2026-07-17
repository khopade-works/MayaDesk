"""Security-headers middleware: baseline browser hardening.

Adds headers that mitigate MIME-sniffing, clickjacking, and referrer leakage.
``Strict-Transport-Security`` is opt-in and only set in production, since
forcing HTTPS during local development over plain HTTP would break it.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

_PERMISSIONS_POLICY = "camera=(), microphone=(), geolocation=()"
_HSTS_VALUE = "max-age=31536000; includeSubDomains"


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Attach baseline security headers to every response.

    :param is_production: When true, also sets ``Strict-Transport-Security``.
    """

    def __init__(self, app: ASGIApp, *, is_production: bool = False) -> None:
        super().__init__(app)
        self._is_production = is_production

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-XSS-Protection"] = "0"
        response.headers["Permissions-Policy"] = _PERMISSIONS_POLICY
        if self._is_production:
            response.headers["Strict-Transport-Security"] = _HSTS_VALUE
        return response
