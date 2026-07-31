# Environments

Pantry runs in named environments that live side by side on one machine.
Local dev on ports 8000/5173 is unchanged and unaffected; the named
environments sit alongside it.

| Environment | Purpose | Frontend | API | Database |
|---|---|---|---|---|
| `silver` | Staging — the stable environment, for checking a change the way a user would meet it | http://localhost:5100 | 8100 | `pantry_silver` |
| `capsule-1` | Lower test environment | http://localhost:5101 | 8101 | `pantry_capsule_1` |
| `capsule-2` | Lower test environment | http://localhost:5102 | 8102 | `pantry_capsule_2` |
| `capsule-3` | Lower test environment | http://localhost:5103 | 8103 | `pantry_capsule_3` |

Each environment has its own database, its own JWT signing key (so a session
from one is not valid in another), and its own ports. Nothing is shared
except the Postgres server itself and the Anthropic API key.

## Using them

```bash
scripts/pantry-env up silver          # start (creates + migrates + seeds on first run)
scripts/pantry-env status             # what's running, and which checkout it runs
scripts/pantry-env logs silver        # tail the backend log (add `frontend` for the UI)
scripts/pantry-env reset capsule-1    # wipe the database back to a clean seed
scripts/pantry-env down silver        # stop
```

A fresh environment is migrated to head and seeded with the local test
account (`a` / `password`) and the starter glossary, so it is immediately
usable and identical every time. `reset` returns it to exactly that state —
the fastest way to retest a flow from zero.

Every environment shows its name in a badge in the bottom-right corner of
the UI, and reports it at `GET /health`. Plain local dev shows no badge.

## Running a branch in an environment

This is the main reason the capsules exist: exercising a branch in a real
stack without evicting dev from its ports.

```bash
scripts/pantry-env up capsule-1 --from /path/to/a/worktree
```

`--from` points an environment at any checkout of this repo — typically a
git worktree — and defaults to the checkout you ran the script from. The
backend runs with `--reload` and the frontend with HMR, so edits in that
checkout are live in the environment.

One constraint: the checkout must include per-environment CORS config
(`settings.cors_origins`, added alongside these environments). A branch cut
before that lands serves an API that only accepts dev's origin, so its
environment's UI cannot call it. The script warns when it detects this —
rebase the branch on master to fix it.

## Configuration

`envs/<name>.env` holds everything specific to one environment: its ports,
database, allowed CORS origin, and signing key. These files are committed —
they contain no secrets.

Shared secrets stay in the gitignored repo-root `.env`, which the launcher
loads first and the environment file then layers on top. So the Anthropic
API key exists in exactly one place, and a worktree with no `.env` of its
own falls back to the main checkout's copy.

The app reads all of this through `Settings` (`backend/app/config.py`);
nothing environment-specific is hardcoded in application code.

## Deploying these for real

The local environments deliberately run uvicorn and Vite directly, because
instant reloads matter more than production fidelity when you're testing a
branch.

The groundwork for hosting them is in place: every environment-specific
value is already an environment variable, and `backend/Dockerfile` and
`frontend/Dockerfile` build deployable images. A hosted environment needs a
Postgres instance, the same variables set in the host's config, and
`alembic upgrade head` run as a release step (deliberately not on container
boot — replicas would race each other).

Note that Vite inlines `VITE_*` values at build time, so the frontend image
is built per environment rather than configured at start:

```bash
docker build --build-arg VITE_API_BASE_URL=https://api.example.com \
             --build-arg VITE_ENV_NAME=silver -t pantry-web:silver frontend/
```
