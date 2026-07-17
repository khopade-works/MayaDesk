"""Application error hierarchy for MayaDesk.

These exceptions carry an HTTP-friendly ``status_code`` so the API layer can
translate them into responses without leaking implementation details. No
framework handlers live here — the API owns HTTP translation.
"""

from __future__ import annotations


class AppError(Exception):
    """Base class for all expected application errors.

    :param message: Human-readable error description.
    :param status_code: HTTP status code the API should respond with.
    """

    status_code: int = 500

    def __init__(self, message: str, *, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def __str__(self) -> str:
        return self.message


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404


class ValidationError(AppError):
    """Raised when input fails domain-level validation."""

    status_code = 422


class ConflictError(AppError):
    """Raised when an action conflicts with current state (e.g. a double-booking)."""

    status_code = 409


class ConfigurationError(AppError):
    """Raised when a required piece of runtime configuration is missing.

    Distinct from a programming bug: the service is healthy but cannot fulfil
    the request until an operator supplies the missing setting (e.g. LiveKit
    credentials). Surfaced as ``503 Service Unavailable``.
    """

    status_code = 503
