# Pantry — Project Plan

A living status tracker for building out the MVP described in `docs/MVP.md`.
Update this file as work completes or plans change — it's the "what's done,
what's next" doc; `docs/MVP.md` stays the stable feature/architecture spec.

## Status: First vertical slice working

Full scaffolding (Docker, Postgres, backend, DB schema, auth, Anthropic
wrapper, frontend shell) plus the first real vertical slice — ingest a
recipe (URL or pasted text) → it's persisted and structured → view it →
save it to the cookbook → see it listed — all verified end-to-end,
including in an actual browser. Next up: the remaining recipe-assistant
features (insights, substitutions, adaptation, scaling, guided cook mode)
(the cookbook vertical slice).

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
- [x] Anthropic wiring: `config.py` reads `ANTHROPIC_API_KEY`/`CLAUDE_MODEL`;
      `services/claude_client.py` builds one shared, cached client — verified:
      a live `claude-opus-5` call through the wrapper returned `"OK"` with
      `stop_reason: end_turn`
- [x] Recipe ingestion skeleton: `url_fetcher` + `jsonld_parser` (no LLM
      dependency), `claude_extractor` (Claude structured-output extraction via
      `messages.parse()` + `ParsedRecipe`), `pipeline.py` (JSON-LD first, falls
      back to Claude), wired into `POST /recipes/ingest` (auth-gated,
      parse-and-return only — no persistence yet). Verified: JSON-LD parser
      against a synthetic schema.org fixture, Claude extraction against
      pasted text, and the full authed route end-to-end (401 without auth,
      400 with neither `url` nor `text`, correct structured JSON otherwise)
- [x] Frontend skeleton: Vite + React + TS scaffold, router shell,
      `api/client.ts`, `AuthContext` (token in localStorage, matching the
      backend's bearer-token contract), login/register pages, protected-route
      redirect. Verified end-to-end in an actual browser: register → login →
      logout → protected-route redirect all work.
      Fixed along the way: the backend had no CORS middleware at all, so the
      browser's preflight `OPTIONS /auth/register` 405'd and registration
      failed with a generic network error — added `CORSMiddleware` allowing
      `http://localhost:5173` (revisit the allow-list once there's a real
      deployment target).
      Note: React Router 7.18.1 has an npm-audit-flagged high-severity
      advisory, but it's RSC-mode-specific (CSRF bypass in server actions) —
      inapplicable to this plain client-side SPA, so left as-is rather than
      downgrading.
      Open decision: JWT lives in `localStorage`, not an httpOnly cookie —
      simpler to wire against the existing Authorization-header backend
      contract, but worth revisiting for XSS hardening later (see Open
      decisions table).
- [x] Cookbook list + ingest UI + recipe detail view — first real vertical
      slice: ingest → view → save. Backend: `POST /recipes/ingest` now
      persists (Recipe/Ingredient/Step rows) and returns a real id instead of
      parse-and-return only; added `GET /recipes/{id}`, `POST
      /recipes/{id}/save` (idempotent), `GET /recipes/cookbook`. Frontend:
      real `IngestPage` (URL or paste-text), `RecipeDetailPage` (structured
      view + Save to Cookbook), `CookbookPage` (saved-recipe list). Verified
      via curl end-to-end (persist, fetch, idempotent save, cookbook list)
      and in an actual browser (ingest → detail page with ingredients/steps →
      save → shows up on /cookbook)
- [x] "Why this works" insight endpoint + UI panel. Backend:
      `generate_recipe_insights` (Claude, structured output) tags relevant
      seeded `GlossaryTerm`s, writes a recipe-specific note per tag, anchors
      to a step/ingredient index or `general`; `persist_recipe_insights`
      resolves indices to real rows (best-effort: unknown slugs/out-of-range
      indices are skipped, not errors); runs at ingestion time, non-blocking.
      Exposed via nested `insights` on `RecipeRead`. Frontend:
      `InsightCallout` component renders each insight (category + glossary
      term name badge, recipe-specific note) inline directly under the
      ingredient/step it's anchored to; unanchored insights surface in a
      "Why this dish works" panel above the ingredients list — not a raw
      data dump. Verified via curl (seared steak + pan sauce: 6 accurate,
      correctly-anchored insights) and in an actual browser end-to-end.
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
| JWT storage | `localStorage` | XSS exposure becomes a real concern before mobile arrives — would mean adding cookie-based auth (httpOnly, CORS `credentials`) instead of the Authorization-header contract |

## Notes

- Backend and frontend directories haven't been created — the "Recipe
  ingestion architecture" and "Data model" sections in `docs/MVP.md` describe
  the intended shape, not existing files.
- Update the checkboxes above as steps complete, and add rows to the open-
  decisions table if new tradeoffs surface during implementation.
- Docker Desktop is now installed and verified (`docker compose up -d db` +
  `pg_isready` both succeed). See `SESSION_LOG.md` for session-by-session
  detail.
