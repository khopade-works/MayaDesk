"""Rate limiting: a slowapi ``Limiter`` keyed by remote address.

The default limit (``RATE_LIMIT_DEFAULT``) applies to every route; individual
routers may layer a stricter limit on top via ``@limiter.limit(...)`` for
sensitive endpoints (e.g. token minting). Limiting can be switched off
entirely for tests/dev via ``RATE_LIMIT_ENABLED``.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from maya_domain.config import get_settings

_settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[_settings.rate_limit_default],
    enabled=_settings.rate_limit_enabled,
)
