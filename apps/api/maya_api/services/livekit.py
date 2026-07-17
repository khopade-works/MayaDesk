"""LiveKit access-token minting.

Server-side generation of short-lived join tokens so the browser can connect to
a LiveKit room where the Maya agent worker is dispatched. Credentials never leave
the backend; the browser only ever receives a signed, scoped JWT.
"""

from __future__ import annotations

from livekit import api

from maya_domain.config import Settings, get_settings
from maya_domain.core.errors import ConfigurationError


def _require_livekit_config(settings: Settings) -> Settings:
    missing = [
        name
        for name, value in (
            ("LIVEKIT_URL", settings.livekit_url),
            ("LIVEKIT_API_KEY", settings.livekit_api_key),
            ("LIVEKIT_API_SECRET", settings.livekit_api_secret),
        )
        if not value
    ]
    if missing:
        raise ConfigurationError(
            f"LiveKit is not configured; missing: {', '.join(missing)}."
        )
    return settings


def mint_join_token(*, room: str, identity: str, name: str | None = None) -> str:
    """Mint a room-scoped LiveKit join JWT for a browser participant."""
    settings = _require_livekit_config(get_settings())
    token = (
        api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret)
        .with_identity(identity)
        .with_name(name or identity)
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
            )
        )
    )
    return token.to_jwt()
