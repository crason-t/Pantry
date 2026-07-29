# Pantry Ticket Tracker

A standalone, single-user "Jira-lite" for tracking Pantry dev work: epics,
tickets with a drag-and-drop kanban board, comments, and an auto-logged
activity feed. It lives in this repo for convenience but is otherwise fully
independent of the Pantry app — separate backend, separate frontend,
separate database, separate ports. It does not sync with GitHub Issues.

No login: this is a local dev tool for one person, so there's no auth layer.
Attribution (reporter/assignee/comment author/activity actor) is a plain
string, defaulting to `"carson"`.

## Running it

```bash
# 1. Start its own Postgres (separate container/volume from Pantry's)
docker compose up -d

# 2. Backend
cd backend
cp ../.env.example ../.env   # first time only
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8010

# 3. Frontend (separate terminal)
cd frontend
cp .env.example .env   # first time only
npm install
npm run dev   # http://localhost:5180
```

Ports (chosen to never collide with Pantry's own dev servers on 8000/5173):
- Backend: `8010`
- Frontend: `5180`
- Postgres: `5434` (host) → `5432` (container)

The Compose project is explicitly named `pantry-standalone-ticket-tracker`
in `docker-compose.yml` — don't remove that `name:` field. Without it,
Compose defaults to this directory's basename (`ticket-tracker`), which
collides with any other worktree/checkout that happens to share the same
directory name.
