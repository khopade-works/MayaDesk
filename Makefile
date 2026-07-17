# ==============================================================================
# MayaDesk — developer Makefile
# Run `make` or `make help` to list available targets.
# ==============================================================================

PYTHON ?= python
PIP    ?= $(PYTHON) -m pip
NPM    ?= npm

.PHONY: help install migrate revision dev-api dev-web dev-agent seed test lint format clean

help: ## Show this help
	@echo "MayaDesk — available targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

install: ## Install Python packages (editable) and web dependencies
	$(PIP) install -e packages/domain -e apps/api -e apps/agent
	cd apps/web && $(NPM) install

migrate: ## Apply Alembic migrations to the configured DATABASE_URL
	cd packages/domain && alembic upgrade head

revision: ## Autogenerate a new Alembic migration (usage: make revision m="message")
	cd packages/domain && alembic revision --autogenerate -m "$(m)"

dev-api: ## Run the FastAPI app with auto-reload on :8000
	uvicorn maya_api.main:app --reload --port 8000

dev-web: ## Run the Next.js dev server on :3000
	cd apps/web && $(NPM) run dev

dev-agent: ## Run the LiveKit worker (Phase 3, skeleton only)
	$(PYTHON) -m maya_agent.worker

seed: ## Seed the database with sample data
	$(PYTHON) -m maya_domain.seed

test: ## Run Python and web test suites
	pytest
	cd apps/web && $(NPM) test

lint: ## Lint Python (ruff) and web (eslint) sources
	ruff check .
	cd apps/web && $(NPM) run lint

format: ## Format Python (ruff) and web sources
	ruff format .
	cd apps/web && $(NPM) run format

clean: ## Remove caches, build artifacts, and local databases
	find . -type d -name '__pycache__' -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache
	rm -f *.db *.db-wal *.db-shm
