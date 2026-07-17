"""A minimal in-process async publish/subscribe bus.

Each subscriber gets its own bounded queue. Publishing never blocks on slow
consumers: if a subscriber's queue is full, its oldest event is dropped so a
stalled dashboard tab cannot back-pressure the publisher.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

_QUEUE_MAXSIZE = 100


class EventBus:
    """Fan-out bus delivering each published event to all live subscribers."""

    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue[dict[str, Any]]] = set()

    async def publish(self, event: dict[str, Any]) -> None:
        for queue in list(self._subscribers):
            if queue.full():
                # Drop the oldest event to make room; never block the publisher.
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:  # pragma: no cover - race with consumer
                    pass
            queue.put_nowait(event)

    def add_subscriber(self) -> asyncio.Queue[dict[str, Any]]:
        """Register and return a new subscriber queue (call before consuming)."""
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=_QUEUE_MAXSIZE)
        self._subscribers.add(queue)
        return queue

    def remove_subscriber(self, queue: asyncio.Queue[dict[str, Any]]) -> None:
        self._subscribers.discard(queue)

    async def subscribe(self) -> AsyncIterator[dict[str, Any]]:
        """Yield events until the consumer stops iterating."""
        queue = self.add_subscriber()
        try:
            while True:
                yield await queue.get()
        finally:
            self.remove_subscriber(queue)

    @property
    def subscriber_count(self) -> int:
        return len(self._subscribers)


_bus = EventBus()


def get_event_bus() -> EventBus:
    """Return the process-wide event bus."""
    return _bus
