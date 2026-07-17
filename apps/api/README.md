# maya-api

MayaDesk HTTP API built on FastAPI.

## Run

```bash
uvicorn maya_api.main:app --reload
```

- `GET /` — service banner.
- `GET /health` — liveness plus a live database connectivity check (503 if the
  database is unreachable).
