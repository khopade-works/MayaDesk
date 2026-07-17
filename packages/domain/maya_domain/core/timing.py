"""Elapsed-time measurement helpers.

Provides a context manager usable in both sync and async code, plus decorators
that log the elapsed milliseconds of a wrapped callable via structlog.
"""

from __future__ import annotations

import functools
import time
from collections.abc import Awaitable, Callable
from types import TracebackType
from typing import Any, TypeVar

from maya_domain.core.logging import get_logger

_logger = get_logger("maya_domain.timing")

F = TypeVar("F", bound=Callable[..., Any])
AF = TypeVar("AF", bound=Callable[..., Awaitable[Any]])


class Timer:
    """Measure elapsed wall-clock time for a block of code.

    Usable as either a synchronous or asynchronous context manager::

        with Timer("db.query"):
            ...

        async with Timer("db.query"):
            ...

    On exit the elapsed time is logged and exposed as :attr:`elapsed_ms`.
    """

    def __init__(self, label: str, *, log: bool = True, **fields: Any) -> None:
        self.label = label
        self._log = log
        self._fields = fields
        self._start: float | None = None
        self.elapsed_ms: float = 0.0

    def _begin(self) -> None:
        self._start = time.perf_counter()

    def _finish(self) -> None:
        start = self._start if self._start is not None else time.perf_counter()
        self.elapsed_ms = (time.perf_counter() - start) * 1000.0
        if self._log:
            _logger.info(
                "timing",
                label=self.label,
                elapsed_ms=round(self.elapsed_ms, 3),
                **self._fields,
            )

    def __enter__(self) -> Timer:
        self._begin()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._finish()

    async def __aenter__(self) -> Timer:
        self._begin()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self._finish()


def timed(label: str | None = None, **fields: Any) -> Callable[[F], F]:
    """Decorator that times a synchronous function and logs the duration."""

    def decorator(func: F) -> F:
        resolved_label = label or func.__qualname__

        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            with Timer(resolved_label, **fields):
                return func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator


def timed_async(label: str | None = None, **fields: Any) -> Callable[[AF], AF]:
    """Decorator that times an async function and logs the duration."""

    def decorator(func: AF) -> AF:
        resolved_label = label or func.__qualname__

        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            async with Timer(resolved_label, **fields):
                return await func(*args, **kwargs)

        return wrapper  # type: ignore[return-value]

    return decorator
