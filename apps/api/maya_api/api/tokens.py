"""Voice access-token endpoint.

The browser calls this to obtain a LiveKit join token and server URL before
connecting to a room. Room and identity are generated when not supplied so a
patient can start a call with no prior state.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from maya_domain.config import get_settings

from maya_api.app.rate_limit import limiter
from maya_api.services.livekit import mint_join_token

router = APIRouter(prefix="/api", tags=["voice"])


class TokenRequest(BaseModel):
    """Optional overrides; any omitted field is generated server-side."""

    room: str | None = Field(default=None, description="Room to join; generated if absent.")
    identity: str | None = Field(default=None, description="Participant identity; generated if absent.")
    name: str | None = Field(default=None, description="Display name for the participant.")


class TokenResponse(BaseModel):
    token: str
    url: str
    room: str
    identity: str


@router.post("/token", response_model=TokenResponse)
@limiter.limit(get_settings().rate_limit_token)
async def create_token(request: Request, body: TokenRequest) -> TokenResponse:
    """Mint a LiveKit join token for a browser patient session.

    Rate-limited more strictly than the global default since this endpoint
    mints credentials (see ``RATE_LIMIT_TOKEN``).
    """
    room = body.room or f"maya-call-{uuid.uuid4().hex[:12]}"
    identity = body.identity or f"patient-{uuid.uuid4().hex[:8]}"
    token = mint_join_token(room=room, identity=identity, name=body.name)
    return TokenResponse(
        token=token,
        url=get_settings().livekit_url or "",
        room=room,
        identity=identity,
    )
