---
name: start-session
description: Use at the start of a Pantry development session, or whenever the user says "start the session", "spin everything up", "start the board", "start the dev servers", or otherwise wants the local dev environment running. Brings up the ticket board (ticket-tracker UI on 5180, API on 8010, its own Postgres) and the Pantry app (backend on 8000, frontend on 5173, pantry-db-1), skipping anything already running, then verifies health and reports the URLs plus a short orientation — in-progress/in-review board tickets and the session log's current state — so the session starts with context.
---

# Start Session

Run this at the start of a Pantry working session (the bookend to
`save-progress`). It has three jobs: get both stacks running, verify they're
actually healthy, and orient the session — what's on the board and where the
last session left off.

Everything here targets the **main checkout**
(`/Users/carson/Claude/Projects/Pantry`), not a worktree — the dev servers
should serve the code the user is actually working on. Starting servers is
not a file edit, so no worktree isolation is needed; run this skill in place.

## Ports and services

| Service                 | Where                        | Port | Check                              |
| ----------------------- | ---------------------------- | ---- | ---------------------------------- |
| Pantry Postgres         | repo root `docker-compose`   | 5432 | `docker ps` → `pantry-db-1`        |
| Pantry backend          | `backend/` (FastAPI)         | 8000 | `GET http://localhost:8000/health` |
| Pantry frontend         | `frontend/` (Vite)           | 5173 | `GET http://localhost:5173`        |
| Tracker Postgres        | `ticket-tracker/`            | 5434 | `docker ps` → `pantry-standalone-ticket-tracker-db-1` |
| Tracker API             | `ticket-tracker/backend/`    | 8010 | `GET http://localhost:8010/health` |
| Board UI                | `ticket-tracker/frontend/`   | 5180 | `GET http://localhost:5180`        |

## 1. Check what's already running — never double-start

Before starting anything, probe every service in one pass:

```bash
curl -s -m 3 http://localhost:8000/health
curl -s -m 3 http://localhost:8010/health
curl -s -m 3 -o /dev/null -w "%{http_code}" http://localhost:5173
curl -s -m 3 -o /dev/null -w "%{http_code}" http://localhost:5180
docker ps --format '{{.Names}} {{.Status}}'
```

Anything that responds is up — leave it alone. Don't kill and restart a
running server, and don't start a second copy on the same port (uvicorn and
Vite will both fail or silently pick a different port, which breaks the
frontend's API base URLs). Only start what's missing. If everything is
already up, skip straight to step 4.

A `/health` response of `{"status": "ok", "db": "unreachable"}` means the
server is up but its Postgres container isn't — start the container, don't
restart the server.

## 2. Start what's missing — Pantry stack

From the repo root, in dependency order:

```bash
docker compose up -d          # pantry-db-1; idempotent, safe when already up
```

Backend — run as a **background** Bash task (`run_in_background: true`),
never a foreground command that would block the session:

```bash
cd backend && uv run alembic upgrade head && uv run uvicorn app.main:app --reload
```

Frontend — also in the background:

```bash
cd frontend && npm run dev
```

`alembic upgrade head` is cheap and idempotent — always run it so the session
never starts against a stale schema. Skip `uv sync` / `npm install` unless
startup fails with a missing-dependency error (`ModuleNotFoundError`, Vite
unable to resolve an import) — then run them and retry once.

## 3. Start what's missing — ticket tracker

Same pattern, from `ticket-tracker/` (details in `ticket-tracker/README.md`):

```bash
cd ticket-tracker && docker compose up -d      # tracker's own Postgres, port 5434
```

```bash
cd ticket-tracker/backend && uv run alembic upgrade head && uv run uvicorn app.main:app --reload --port 8010
```

```bash
cd ticket-tracker/frontend && npm run dev      # serves on 5180
```

First-time-only setup the README calls out: `cp .env.example .env` in
`ticket-tracker/` (for the backend) and in `ticket-tracker/frontend/`. If a
server dies immediately with a missing-settings/env error, that's the fix.

## 4. Verify before reporting

Re-run the step-1 probes until all four HTTP checks pass. Give the servers a
few seconds — poll, don't declare failure on the first refused connection.
If a server still isn't up after ~30 seconds, read its background-task output
and report the actual error; don't paper over a dead service with a green
summary.

## 5. Orient the session

With the board up, pull just enough context to start working:

- `GET http://localhost:8010/tickets` — list tickets that are `in_progress`
  or `in_review` (work mid-flight from last session), and the top few
  `todo`/`backlog` items by priority.
- Read the "Current State" section at the top of `SESSION_LOG.md` — where
  the last session left off and what it said was next.

Don't reconcile, close, or edit anything here — that's `save-progress`'s
job at the other end of the session. This step is read-only.

## Output

End with a short, scannable status block:

- Each service with its URL and up/started/failed state — call out anything
  that was already running vs. newly started, and any failure with its
  actual error.
- Board: in-progress and in-review tickets by key and title; top backlog
  candidates.
- One or two lines from the session log's current state on what's next.

That summary is the point of the skill — the user should be able to start
working (or pick a ticket) without running anything else.
