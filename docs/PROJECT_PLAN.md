# Pantry — Project Plan

A living status tracker for building out the MVP described in `docs/MVP.md`.
Update this file as work completes or plans change — it's the "what's done,
what's next" doc; `docs/MVP.md` stays the stable feature/architecture spec.

## Status: Scaffolding

Repo has a README, `.gitignore`, `CLAUDE.md`, and the MVP spec. No backend or
frontend code exists yet.

## Build sequence

- [x] `git init` + initial commit (README, `.gitignore`, `docs/MVP.md`)
- [x] `CLAUDE.md`
- [ ] `docker-compose.yml` + `.env.example` for local Postgres — verify
      `docker compose up -d db` works before writing app code
- [ ] Backend skeleton: FastAPI app, `config.py` (env-based settings),
      `GET /health` (pings DB) — verify `uvicorn` runs and reaches Postgres
- [ ] DB models + Alembic migration for `User`, `Recipe`, `Ingredient`,
      `Step`, `SavedRecipe` — verify `alembic upgrade head` applies cleanly
- [ ] Auth: register/login endpoints, password hashing, JWT issue/verify,
      `get_current_user` dependency — verify via Swagger UI (`/docs`) or `curl`
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
- `docker-compose.yml` and root/`frontend` `.env.example` files now exist,
  but the "verify `docker compose up -d db` works" half of that checklist
  item is still outstanding — the Docker CLI isn't installed in this dev
  environment. Don't check that box until it's actually been run somewhere
  Docker is available. See `SESSION_LOG.md` for session-by-session detail.
