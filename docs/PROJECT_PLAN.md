# Pantry — Project Plan

A living status tracker for building out the MVP described in `docs/MVP.md`.
Update this file as work completes or plans change — it's the "what's done,
what's next" doc; `docs/MVP.md` stays the stable feature/architecture spec.

## Status: Scaffolding

Repo has a README, `.gitignore`, `CLAUDE.md`, and the MVP spec. Docker
Desktop, Postgres, the FastAPI backend skeleton, the full DB schema (via
Alembic), and JWT auth (register/login/`/auth/me`) are all verified working
locally. No Anthropic wiring, ingestion code, or frontend yet.

## Build sequence

- [x] `git init` + initial commit (README, `.gitignore`, `docs/MVP.md`)
- [x] `CLAUDE.md`
- [x] `docker-compose.yml` + `.env.example` for local Postgres — verified:
      Docker Desktop installed, `docker compose up -d db` starts `pantry-db-1`
      and `pg_isready` confirms it accepts connections
- [x] Backend skeleton: FastAPI app, `config.py` (env-based settings),
      `GET /health` (pings DB) — verified: `uv sync` on Python 3.12,
      `uvicorn` boots, `GET /health` returns `{"status": "ok", "db": "ok"}`
- [x] DB models + Alembic migration for `User`, `Recipe`, `Ingredient`,
      `Step`, `GlossaryTerm`, `RecipeInsight`, `SavedRecipe` (updated per the
      glossary/insight-callouts rewrite in `docs/MVP.md`) — verified:
      `alembic upgrade head` creates all 7 tables cleanly, and
      `app/seed_glossary.py` idempotently seeds 8 starter glossary terms
- [x] Auth: register/login endpoints, password hashing, JWT issue/verify,
      `get_current_user` dependency — verified via `curl`: register, duplicate
      email rejected (400), login issues a working JWT, `/auth/me` returns the
      user with a valid token and 401s without one, wrong password 401s.
      Note: switched from `passlib[bcrypt]` to the `bcrypt` package directly —
      passlib 1.7.4 is unmaintained and breaks against `bcrypt` 5.x
- [ ] Anthropic wiring: `config.py` reads `ANTHROPIC_API_KEY`/`CLAUDE_MODEL`;
      `services/claude_client.py` builds one shared client — confirm
      connectivity with a throwaway test call
- [ ] Recipe ingestion skeleton: `url_fetcher` + `jsonld_parser` (no LLM
      dependency), `claude_extractor` stub with its structured-output schema,
      wired into a placeholder `POST /recipes/ingest`
- [ ] Frontend skeleton: Vite + React + TS scaffold, router shell,
      `api/client.ts`, login/register pages wired end-to-end against the
      backend auth endpoints
- [ ] Cookbook list + ingest UI + recipe detail view — first real vertical
      slice: ingest → view → save
- [ ] "Why this works" insight endpoint + UI panel
- [ ] Ingredient substitution endpoint + UI
- [ ] Equipment/method adaptation endpoint + UI
- [ ] Serving-scale endpoint + UI
- [ ] Guided step-by-step cook-mode UI (purely frontend, consumes steps
      already returned by the recipe-detail endpoint)
- [ ] Polish: error handling, loading states, minimal styling pass

## Open decisions to revisit

These were made as defaults during initial planning — flag here if reality
argues for a different choice:

| Decision | Current choice | Reconsider if... |
|---|---|---|
| Database | PostgreSQL | Multi-user need never materializes and SQLite's zero-ops tradeoff looks better in hindsight |
| Auth | Rolled JWT | Mobile app arrives sooner than expected and a hosted provider's RN SDK saves real time |
| Frontend framework | Vite SPA | SEO/public pages become a requirement |
| Serving-scale logic | Hybrid: math for linear quantities, LLM pass for non-linear items (leavening, spice, time) | Pure math turns out sufficient in practice — simpler, can drop the LLM call |

## Notes

- Backend and frontend directories haven't been created — the "Recipe
  ingestion architecture" and "Data model" sections in `docs/MVP.md` describe
  the intended shape, not existing files.
- Update the checkboxes above as steps complete, and add rows to the open-
  decisions table if new tradeoffs surface during implementation.
- Docker Desktop is now installed and verified (`docker compose up -d db` +
  `pg_isready` both succeed). See `SESSION_LOG.md` for session-by-session
  detail.
