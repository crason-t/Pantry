# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Manual note added by Carson, call this out at the beginning of the next session no matter what.

Here are the things you should run now:
1. Here's a bug I found - [Image #1]. When I ingested the recipe it listed the ingredient names sometimes including their measurement too. I edited the first one to look proper. Paste an image of the ingredients table.
2. Save progress on all jobs that have not run it yet and push all changes
3. Let's start working on redesigning the cookbook tab. Right now the main page for cookbook looks really thrown together.
4. Set up a design system using Claude Design

## Project status

Pantry is in early scaffolding — only `README.md`, `.gitignore`, and `docs/MVP.md` exist. No backend or frontend code has been written yet, so there are no build/lint/test commands to run. Once the backend (`backend/`) and frontend (`frontend/`) skeletons described below exist, this file should be updated with the actual commands (e.g. `uvicorn app.main:app --reload`, `alembic upgrade head`, `npm run dev`) rather than the planned ones listed here.

## What this project is

A recipe assistant: ingest a recipe (URL or pasted text), reformat it into a scannable structure, explain the culinary "why" behind it, suggest ingredient substitutions and equipment/method adaptations, scale servings, and guide the user step-by-step through cooking. Recipes save to a personal cookbook.

Long-term vision is a full home pantry/inventory + recipe + grocery-budget assistant; this repo currently scopes only the recipe-assistant MVP. Full feature list, explicit non-goals, and the data model are in `docs/MVP.md` — read that file before making architectural decisions, and update it when decisions change.

## Planned architecture (not yet built)

- **Backend**: FastAPI (Python), chosen for async support (LLM calls + URL fetches) and because Pydantic validation pairs naturally with Claude's structured-output JSON schemas.
- **Frontend**: Vite + React + TypeScript, a plain SPA (not Next.js) — the app lives entirely behind login, so there's no SSR/SEO need, and a plain SPA keeps a clean API boundary that a future React Native app can reuse.
- **Database**: PostgreSQL via Docker Compose.
- **Auth**: Rolled JWT auth (`bcrypt` + `python-jose` + `OAuth2PasswordBearer`) rather than a hosted provider — a deliberate choice to keep everything transparent and dependency-free for a single-user MVP. Uses `bcrypt` directly, not `passlib` — passlib 1.7.4 is unmaintained and breaks against `bcrypt` 5.x.
- **LLM**: Anthropic Claude API via the official `anthropic` Python SDK, default model `claude-opus-5` (configurable via `CLAUDE_MODEL` env var so individual call sites can be swapped independently).

The backend is meant to stay a clean, reusable JSON API — not entangled with the web frontend — because a mobile (React Native) client is planned to consume the same API later.

### Recipe ingestion pipeline (planned shape)

Two ingestion paths converge on one internal `ParsedRecipe` schema before persistence:
- **URL**: fetch the page → check for embedded schema.org JSON-LD `Recipe` data (reliable, no LLM needed) → fall back to a Claude structured-output extraction call if JSON-LD is absent or incomplete.
- **Pasted text**: always goes through the Claude extraction call (no structured markup to check).

### Data model (planned)

`User`, `Recipe` (with child `Ingredient` and `Step` rows, not JSON blobs, so scaling/display logic can operate on typed data), and `SavedRecipe` as the cookbook join table. Substitutions and adaptations are computed on demand via Claude, not persisted, for MVP. Full field list in `docs/MVP.md`.

## Ticket discipline

Remaining MVP work is tracked as GitHub Milestones (one per feature area) with
one Issue per milestone, in the [Pantry](https://github.com/crason-t/Pantry)
repo. `docs/PROJECT_PLAN.md` stays the narrative build-sequence checklist —
the milestones/issues are the enforceable version of the same plan, not a
replacement for it.

- A **commit-msg hook** (`.githooks/commit-msg`, wired via
  `git config core.hooksPath .githooks`) rejects any commit whose message
  doesn't reference an issue number (`#3`). Reference the issue you're
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
