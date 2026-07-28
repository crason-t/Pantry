# Pantry — Session Log

## Current State (as of 2026-07-28)

- Repo scaffolding committed: README, `.gitignore`, `CLAUDE.md`, `docs/MVP.md`,
  `docs/PROJECT_PLAN.md`. Still pre-code — no `backend/` and no real
  `frontend/` app yet.
- New this session, **uncommitted**:
  - `.claude/skills/save-progress/SKILL.md` — this skill, which maintains
    this file.
  - `docker-compose.yml` + root `.env.example` — single Postgres 16 service
    (`pantry`/`pantry`/`pantry` on `5432`); env covers `DATABASE_URL`,
    `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, JWT settings.
  - `frontend/.env.example` (`VITE_API_BASE_URL`) — no actual Vite project
    scaffolded yet, just the env stub.
  - `docs/MVP.md` substantially rewritten (modified in place, not yet
    committed) — see History below.
- `docker-compose.yml`/`.env.example` are **unverified**: the Docker CLI
  isn't installed in this dev environment, so `docker compose up -d db`
  (required by `docs/PROJECT_PLAN.md` before writing app code) hasn't
  actually been run.

## In progress / blockers

- `docs/MVP.md` rewrite is uncommitted — review and commit once settled.
- Docker verification step is blocked here by no local Docker install; needs
  to happen on a machine/environment that has Docker.

## Next steps

- Commit the `docs/MVP.md` rewrite along with `docker-compose.yml` and both
  `.env.example` files.
- Verify `docker compose up -d db` works somewhere Docker is available, then
  check off that item in `docs/PROJECT_PLAN.md`.
- Start the backend skeleton (FastAPI app, `config.py`, `GET /health`) per
  `docs/PROJECT_PLAN.md`'s build sequence.

---

## History

### 2026-07-28
**Did:**
- Created `.claude/skills/save-progress/SKILL.md` — a skill invoked at the
  end of a session ("save progress", "wrap up") that updates this file: an
  overwritten "Current State" snapshot plus a prepended dated history entry.
  It's told to reconstruct what happened from `git status`/`diff`/`log`
  rather than trusting conversation memory alone, and to keep
  `docs/PROJECT_PLAN.md` in sync rather than duplicating it.
- (Untracked, already present when this session started) `docker-compose.yml`
  + root `.env.example`: single Postgres 16 service; `.env.example` covers
  `DATABASE_URL`, `ANTHROPIC_API_KEY`, `CLAUDE_MODEL`, JWT settings.
  `frontend/.env.example` (`VITE_API_BASE_URL`) also present — no Vite
  project scaffolded yet.
- `docs/MVP.md` substantially rewritten for the "why this dish works"
  feature: replaced the single cached `why_it_works` text field with a
  two-part design — a shared, curated glossary (`GlossaryTerm`: flavor /
  technique / reaction categories, fixed reference data) plus per-recipe
  `RecipeInsight` rows generated at ingestion time (tags a glossary term,
  adds a recipe-specific note, optionally anchored to a specific
  Step/Ingredient). Inspired by cookwell.com's recipe breakdowns.

**Decisions:**
- The glossary is the one deliberate exception to "don't persist LLM output
  for MVP" — its content is fixed domain knowledge, seeded once (migration/
  fixture), not regenerated per recipe ingestion.
- Insights are anchored inline to specific steps/ingredients where possible,
  rather than surfaced as a single dumped paragraph.

**Next:** Commit the `docs/MVP.md` rewrite and new config files; verify
Docker; start the backend skeleton.

**Open questions / blockers:** Docker CLI isn't installed in this
environment — `docker compose up -d db` still needs verifying elsewhere
before backend code-writing starts, per `docs/PROJECT_PLAN.md`.
