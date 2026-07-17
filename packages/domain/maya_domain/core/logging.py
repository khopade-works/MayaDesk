"""Structured logging configuration for MayaDesk.

Uses ``structlog`` with a JSON renderer in production and a human-friendly
console renderer in development. Call :func:`configure_logging` once during
application startup, then obtain loggers via :func:`get_logger`.
"""

from __future__ import annotations

import logging
import sys
from typing import Any

import structlog

_LEVELS: dict[str, int] = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warning": logging.WARNING,
    "warn": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}


def _resolve_level(level: str) -> int:
    return _LEVELS.get(level.strip().lower(), logging.INFO)


def configure_logging(level: str = "info", env: str = "development") -> None:
    """Configure the stdlib logging bridge and structlog processors.

    :param level: Log level name (e.g. ``"info"``, ``"debug"``).
    :param env: Deployment environment; production selects the JSON renderer.
    """
    numeric_level = _resolve_level(level)
    is_production = env.strip().lower() in {"production", "prod"}

    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=numeric_level,
    )

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    renderer: structlog.types.Processor
    if is_production:
        shared_processors.append(structlog.processors.format_exc_info)
        renderer = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(numeric_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None, **initial_values: Any) -> Any:
    """Return a bound structlog logger, optionally namespaced by ``name``."""
    logger = structlog.get_logger(name)
    if initial_values:
        return logger.bind(**initial_values)
    return logger
