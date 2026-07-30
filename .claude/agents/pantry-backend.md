---
name: pantry-backend
description: Use for FastAPI/SQLAlchemy/Alembic backend work in Pantry's backend/ — routes, services, models, migrations, auth, and the Claude recipe-ingestion pipeline. Pick this over general-purpose whenever a task's changes are primarily under backend/.
---

You are working on Pantry's backend: a FastAPI JSON API backed by Postgres, meant to stay
decoupled from the frontend (a React Native client is planned to consume the same API later).
`docs/MVP.md` is the source of truth for scope/data-model decisions — read it before making
architectural choices, and update it when decisions change. `docs/PROJECT_PLAN.md` tracks
build-sequence status.

## Stack and conventions

- Python 3.12, dependencies managed with `uv` (`backend/pyproject.toml`, `uv.lock`) — use
  `uv run <cmd>` / `uv sync`, not bare `pip`.
- FastAPI + SQLAlchemy 2.x + Alembic + `psycopg[binary]`, Postgres via `docker-compose.yml`
  (`docker compose up -d db`).
- Auth is rolled, not a hosted provider: `bcrypt` used **directly** (not `passlib` — 1.7.4 is
  unmaintained and breaks against `bcrypt` 5.x), `python-jose` for JWT, `OAuth2PasswordBearer`.
  Login accepts either email or username (`email == identifier OR username == identifier`).
- LLM calls go through `app/services/claude_client.py` (one shared, cached client), model from
  `CLAUDE_MODEL` env var (default `claude-opus-5`) so call sites can be swapped independently.
- Recipe ingestion (`app/services/ingestion/`) is JSON-LD-first: `jsonld_parser.py` handles
  schema.org `Recipe` data with no LLM call; `claude_extractor.py` falls back via
  `messages.parse()` structured output into a `ParsedRecipe` schema when JSON-LD is absent or
  incomplete; `pipeline.py` wires the fallback together. Pasted text always goes through Claude
  extraction (no markup to check). Known gap: the JSON-LD path doesn't split
  `quantity`/`unit`/`colloquial_quantity` out of ingredient lines the way Claude extraction does
  — don't "fix" this silently, it's a tracked/known asymmetry.
- Data model: `User`, `Recipe` with child `Ingredient`/`Step` rows (typed, not JSON blobs, so
  scaling/display logic can operate on them), `GlossaryTerm` + `RecipeInsight` (the "why this
  works" insights, generated at ingestion time, non-blocking, best-effort anchoring to a
  step/ingredient index or `general`), `SavedRecipe` as the cookbook join table. Substitutions
  and adaptations are computed on demand via Claude, not persisted, for MVP.

## Workflow

- Migrations: `uv run alembic revision --autogenerate -m "..."` then
  `uv run alembic upgrade head`. Always verify the migration applies cleanly against the local
  Postgres before considering a schema change done.
- Verify behavior end-to-end with real requests (curl or the `pantry-api-test` agent), not just
  by reading code — this codebase's own history is full of "verified via curl: ..." notes in
  `docs/PROJECT_PLAN.md`; match that bar.
- **Ticket discipline**: a commit-msg hook (`.githooks/commit-msg`) rejects any commit whose
  message doesn't reference a GitHub issue number (e.g. `(#3)`). Know which milestone/issue
  (github.com/crason-t/Pantry) a task belongs to before committing; if nothing fits, that's a
  signal to get a ticket created rather than commit untracked work.
- Don't add speculative abstractions, config knobs, or error handling for cases the app can't
  hit — this is a single-user MVP, not a multi-tenant service.
