"""In-process event bus for dashboard realtime updates.

Cross-process events (from the voice agent) arrive via the internal HTTP
endpoint and are republished here; WebSocket clients subscribe to the same bus.
Redis pub/sub is the multi-instance production upgrade behind this same seam.
"""

from maya_api.events.bus import EventBus, get_event_bus
from maya_api.events.types import DashboardEvent

__all__ = ["EventBus", "get_event_bus", "DashboardEvent"]
