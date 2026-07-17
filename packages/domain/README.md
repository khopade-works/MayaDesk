# maya-domain

Shared domain package for MayaDesk. Provides:

- `maya_domain.config` — typed application settings (`Settings`, `get_settings`).
- `maya_domain.core` — logging, errors, request-context, and timing helpers.
- `maya_domain.database` — SQLAlchemy 2.0 async engine, session factory, and health `ping()`.
- `maya_domain.models` — declarative `Base` (concrete models arrive in Phase 2).

Alembic is wired for the async engine and targets `maya_domain.database.base.Base.metadata`.
