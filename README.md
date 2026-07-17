# MayaDesk

MayaDesk is an AI healthcare voice receptionist. Its agent, **Maya**, answers calls in the browser over real-time voice, triages the caller's intent, books or reschedules appointments, and escalates anything that looks like an emergency to a human — all while a staff dashboard shows the conversation and call state live.

## ⚠️ HIPAA-aware, NOT HIPAA-compliant

This project is **HIPAA-aware** in its design (it is built with PHI handling in mind), but it is **NOT HIPAA-compliant** and must not be used with real patient data.

- The free-tier providers used here (LiveKit, Groq) do **not** offer Business Associate Agreements (BAAs) on their free tiers.
- Use **synthetic / fake data only** for development, demos, and testing.
- **Never** deploy this project, in its current form, against real Protected Health Information (PHI).

Achieving genuine HIPAA compliance requires signed BAAs with every vendor in the data path, infrastructure hardening, audit logging, and a compliance review — none of which this repository provides out of the box.

## Architecture overview

MayaDesk is a monorepo with two Python runtimes and one Next.js frontend, sharing a common domain layer:

- **`packages/domain`** — shared Python package `maya_domain`: config, core business logic, and the database layer (SQLAlchemy models + Alembic migrations). Both Python runtimes depend on it so the schema and domain rules live in exactly one place.
- **`apps/api`** — FastAPI service `maya_api`. The REST/WebSocket backend for the staff dashboard and any server-side orchestration.
- **`apps/agent`** — LiveKit worker `maya_agent`. Joins voice rooms as the real-time conversational agent (Phase 3, currently a skeleton).
- **`apps/web`** — Next.js (App Router) frontend: the in-browser voice UI callers use to talk to Maya, and the staff dashboard.

```
                 ┌─────────────────────┐
                 │   apps/web (Next.js)│
                 │  voice UI + staff   │
                 │      dashboard      │
                 └──────────┬──────────┘
                            │ HTTP / WebSocket / LiveKit
              ┌─────────────┴─────────────┐
              │                           │
    ┌─────────▼─────────┐      ┌──────────▼──────────┐
    │   apps/api          │      │   apps/agent          │
    │   maya_api (FastAPI) │      │   maya_agent (LiveKit) │
    └─────────┬─────────┘      └──────────┬──────────┘
              │                           │
              └─────────────┬─────────────┘
                            │
                 ┌──────────▼──────────┐
                 │  packages/domain      │
                 │  maya_domain           │
                 │  config · core · db    │
                 └──────────┬──────────┘
                            │
                 ┌──────────▼──────────┐
                 │  DATABASE_URL          │
                 │  sqlite (dev) /        │
                 │  postgres (prod)       │
                 └──────────────────────┘
```

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | Next.js (App Router), React |
| API backend | FastAPI (`maya_api`) |
| Voice agent | LiveKit Agents worker (`maya_agent`) |
| LLM / STT | Groq (`llama-3.3-70b-versatile`, `whisper-large-v3`) |
| Real-time transport | LiveKit |
| Domain / ORM | SQLAlchemy (async), shared `maya_domain` package |
| Migrations | Alembic (config lives in `packages/domain`) |
| Database (dev) | SQLite (`aiosqlite`) |
| Database (prod) | PostgreSQL (`asyncpg`) — one-line env var swap |
| Language / runtime | Python 3.11+, Node.js |

## Folder structure

```
MayaDesk/
├── packages/
│   └── domain/          # maya_domain: config, core, database, Alembic migrations
├── apps/
│   ├── api/              # maya_api: FastAPI backend
│   ├── agent/             # maya_agent: LiveKit worker (Phase 3, skeleton)
│   └── web/               # Next.js App Router frontend + staff dashboard
├── .env.example          # environment variable template (copy to .env)
├── Makefile               # dev workflow targets (install, migrate, dev-api, ...)
├── docker-compose.yml      # local dev services (api, web, optional postgres)
└── README.md
```

## Quickstart

```bash
# 1. Copy the environment template and fill in real values
cp .env.example .env

# 2. Install Python (editable) and web dependencies
make install

# 3. Apply database migrations (SQLite by default, no extra setup needed)
make migrate

# 4. Run the API and the web app (in separate terminals)
make dev-api    # FastAPI on http://localhost:8000
make dev-web    # Next.js on http://localhost:3000
```

Run `make help` at any time to see all available targets.

## Database: SQLite by default, Postgres is a one-line swap

`DATABASE_URL` defaults to `sqlite+aiosqlite:///./maya.db` for zero-friction local development. Because `packages/domain` accesses the database exclusively through SQLAlchemy's async engine, moving to Postgres in production is a single environment variable change — swap `DATABASE_URL` for a `postgresql+asyncpg://...` URL (see the commented-out `postgres` service in `docker-compose.yml`) and re-run `make migrate`. No application code changes required.

## Phase roadmap

- [x] **Phase 1 — Architecture**: monorepo layout, shared domain package, root DX tooling.
- [ ] **Phase 2 — Domain & Data**: core models, migrations, seed data.
- [ ] **Phase 3 — Voice Agent**: LiveKit worker, Groq STT/LLM pipeline, call handling.
- [ ] **Phase 4 — API**: FastAPI endpoints for scheduling, triage, and escalation.
- [ ] **Phase 5 — Web Voice UI**: in-browser calling experience for patients.
- [ ] **Phase 6 — Staff Dashboard**: real-time call/session monitoring for staff.
- [ ] **Phase 7 — Scheduling & Booking**: appointment lifecycle end-to-end.
- [ ] **Phase 8 — Hardening**: testing, observability, error handling at scale.
- [ ] **Phase 9 — Deployment**: production infrastructure, Postgres cutover, CI/CD.
