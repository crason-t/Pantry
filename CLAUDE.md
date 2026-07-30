# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project status

Backend and frontend are fully scaffolded and working end-to-end: auth,
recipe ingestion (URL or pasted text, via Claude), "why this dish works"
insights, recipe tips, and cookbook save/list. See `docs/PROJECT_PLAN.md`'s
build-sequence checklist for exactly what's done vs. open, and
`SESSION_LOG.md` for session-by-session detail.

Local dev commands:

```
docker compose up -d                                # Postgres (pantry-db-1)
cd backend && uv sync && uv run alembic upgrade head
uv run python -m app.seed_glossary                  # starter glossary terms
uv run uvicorn app.main:app --reload                # http://localhost:8000
cd frontend && npm install && npm run dev            # http://localhost:5173
npm run build                                        # tsc -b && vite build
npm run lint                                         # oxlint
```

Repo also contains `ticket-tracker/` — a separate, standalone "Jira-lite"
dev-workflow tool (own backend/frontend/Postgres/ports, no auth). It shares
this repo for convenience but is unrelated to the recipe app; see
`ticket-tracker/README.md` for how to run it. Don't confuse its models/routes
with Pantry's own — they don't share code, DB, or ports.

## What this project is

A recipe assistant: ingest a recipe (URL or pasted text), reformat it into a scannable structure, explain the culinary "why" behind it, suggest ingredient substitutions and equipment/method adaptations, scale servings, and guide the user step-by-step through cooking. Recipes save to a personal cookbook.

Long-term vision is a full home pantry/inventory + recipe + grocery-budget assistant; this repo currently scopes only the recipe-assistant MVP. Full feature list, explicit non-goals, and the data model are in `docs/MVP.md` — read that file before making architectural decisions, and update it when decisions change.

## Architecture

- **Backend**: FastAPI (Python), chosen for async support (LLM calls + URL fetches) and because Pydantic validation pairs naturally with Claude's structured-output JSON schemas.
- **Frontend**: Vite + React + TypeScript, a plain SPA (not Next.js) — the app lives entirely behind login, so there's no SSR/SEO need, and a plain SPA keeps a clean API boundary that a future React Native app can reuse.
- **Database**: PostgreSQL via Docker Compose.
- **Auth**: Rolled JWT auth (`bcrypt` + `python-jose` + `OAuth2PasswordBearer`) rather than a hosted provider — a deliberate choice to keep everything transparent and dependency-free for a single-user MVP. Uses `bcrypt` directly, not `passlib` — passlib 1.7.4 is unmaintained and breaks against `bcrypt` 5.x.
- **LLM**: Anthropic Claude API via the official `anthropic` Python SDK, default model `claude-opus-5` (configurable via `CLAUDE_MODEL` env var so individual call sites can be swapped independently).

The backend is meant to stay a clean, reusable JSON API — not entangled with the web frontend — because a mobile (React Native) client is planned to consume the same API later.

### Recipe ingestion pipeline

Two ingestion paths converge on one internal `ParsedRecipe` schema before persistence:
- **URL**: fetch the page → check for embedded schema.org JSON-LD `Recipe` data (reliable, no LLM needed) → fall back to a Claude structured-output extraction call if JSON-LD is absent or incomplete.
- **Pasted text**: always goes through the Claude extraction call (no structured markup to check).

### Data model

`User`, `Recipe` (with child `Ingredient` and `Step` rows, not JSON blobs, so scaling/display logic can operate on typed data), and `SavedRecipe` as the cookbook join table, plus `GlossaryTerm`/`RecipeInsight`/`RecipeTip` for the "why this works" feature. Substitutions and adaptations are computed on demand via Claude, not persisted, for MVP. Full field list in `docs/MVP.md`.

## Ticket discipline

Day-to-day work is planned and tracked on the local **ticket board**
(`ticket-tracker/` — UI http://localhost:5180, API http://localhost:8010;
see `ticket-tracker/README.md` to start it). GitHub Milestones/Issues in the
[Pantry](https://github.com/crason-t/Pantry) repo remain the commit/release
layer, and `docs/PROJECT_PLAN.md` stays the narrative build-sequence
checklist.

### Board rules (apply to Claude-created and Carson-created tickets alike)

- **Every bug, feature, or other large code change gets a board ticket
  before implementation starts.** Create it via the UI or the API:
  `POST http://localhost:8010/tickets` with `title`, `description`,
  `acceptance_criteria`, `labels` (e.g. `["bug"]`, `["feature"]`,
  `["chore"]`), `priority`, and `epic_id`.
- **Acceptance criteria are required** — the API rejects ticket creation
  without `acceptance_criteria`. Write 2–5 concrete, checkable statements
  defining "done", not a restatement of the title.
- **Link the ticket to an epic when a relevant one exists**
  (`GET http://localhost:8010/epics`). Epics mirror the GitHub milestones;
  if work fits no existing epic, create a new epic (and the matching GitHub
  milestone) rather than leaving the ticket unlinked.
- Move status as work progresses (`PATCH /tickets/{id}`): `in_progress`
  when starting, `in_review` when a PR opens, `done` when it merges — and
  add a comment linking the PR.
- If the tracker isn't running, start it (see `ticket-tracker/README.md`)
  rather than skipping the ticket.

### GitHub layer (commits and releases)

- A **commit-msg hook** (`.githooks/commit-msg`, wired via
  `git config core.hooksPath .githooks`) rejects any commit whose message
  doesn't reference a GitHub issue number (`#3`). Reference the issue you're
  closing or advancing in every commit message.
- When a milestone is closed, `.github/workflows/milestone-release.yml`
  automatically tags the default branch and cuts a GitHub Release listing
  everything that shipped in it.
- `.github/workflows/require-milestone.yml` comments on any new issue that
  isn't assigned to a milestone yet, as a reminder to fix it.
- If a piece of work genuinely doesn't fit an existing milestone, open a new
  issue under the right milestone (or propose a new one) before writing the
  code — don't let untracked work happen because no ticket existed yet.

## Where to look first

- `docs/MVP.md` — feature spec, explicit non-goals, architecture decision log, data model, ingestion architecture. This is the source of truth for scope and design decisions.
- `docs/PROJECT_PLAN.md` — build-sequence checklist and open-decisions table; cross-references the GitHub issues above for remaining work.
- `README.md` — one-paragraph project summary and current status.
