"""ASGI entrypoint: ``uvicorn maya_api.main:app``."""

from __future__ import annotations

from maya_api.app.factory import create_app

app = create_app()
