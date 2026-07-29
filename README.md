# Pantry

A recipe assistant: ingest a recipe (URL or pasted text), get it reformatted into
a scannable structure, understand the culinary "why" behind it, get ingredient
substitutions and equipment/method adaptations, scale servings, and get guided
step-by-step through cooking it. Save recipes to a personal cookbook.

Long-term vision is a full home pantry/inventory + recipe + grocery-budget
assistant; this repo currently scopes only the recipe-assistant MVP.

See `docs/MVP.md` for the full feature spec and architecture decisions.

## Status

Backend and frontend are built and working end-to-end (auth, recipe
ingestion, "why this dish works" insights, ingredient substitutions,
per-user ingredient customization, cookbook save/list); several features
remain (adaptations, serving-scale, guided cook mode). See
`docs/PROJECT_PLAN.md` for the build-sequence checklist and
`SESSION_LOG.md` for session-by-session detail.

## Local dev setup

```
docker compose up -d                              # postgres
cd backend && uv sync && uv run alembic upgrade head
uv run python -m app.seed_glossary                # starter glossary terms
uv run python -m app.seed_test_user                # fixed local test account
uv run uvicorn app.main:app --reload               # http://localhost:8000

cd frontend && npm install && npm run dev          # http://localhost:5173
```

`app/seed_test_user.py` creates a fixed, clearly-labeled **test account**
(`test@mail.com`, username `a`, password `password`) for local dev/testing —
it's not a real user. These match the account long-standing dev environments
already have, so the documented login works everywhere. The seed is
idempotent, so it's safe to re-run against any environment (including a
fresh DB in a new worktree) without touching an existing account's password.
