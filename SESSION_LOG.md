# Pantry — Session Log

## Current State (as of 2026-07-29)

Manual note added by Carson, call this out at the beginning of the next session no matter what.

Here are the things you should run now:
1. Here's a bug I found - [Image #1]. When I ingested the recipe it listed the ingredient names sometimes including their measurement too. I edited the first one to look proper. Paste an image of the ingredients table.
2. Save progress on all jobs that have not run it yet and push all changes
3. Let's start working on redesigning the cookbook tab. Right now the main page for cookbook looks really thrown together.
4. Set up a design system using Claude Design
5. Finish creating the Jira replica for ticket tracking and make sure it's actually hooked up to the project structure.
6. Create a skill to get the environment ready for development just by running a simple skill in the right directory. Should spin up things like a few localhost instances with reserved ports for development and testing. Let's also assign names to these and the browser tab name changes depending on the specific feature being tested. Like if a localhost instance is meant to test changes to the Recipe page, it should be called something descriptive like Recipe Rework Test. There should be a page dedicated to navigating between these localhost instances too

Checked in after surfacing this list (2026-07-29, same session as the
`f6bfb24` reconciliation): item 1 needs a screenshot Carson hasn't
provided yet, and when asked which of 3/4/5 to start next he initially
said "Done for now" — no pick made at that point. He later came back and
picked item 5 specifically (ticket tracker independence), which is now
done as PR #24. Item 2 is done (see `f6bfb24`). Items 3, 4, 6 and the
item-1 screenshot are still outstanding — don't re-ask, just wait for
direction.

- Backend + frontend are fully scaffolded and working end-to-end (FastAPI +
  Postgres, Vite/React/TS SPA): auth, recipe ingestion (URL or pasted text,
  via Claude), "Keys of the recipe" / "Why this dish works" insights, recipe
  tips, cookbook save/list. See `docs/PROJECT_PLAN.md`'s build-sequence
  checklist for the authoritative status — everything through "Why this
  works" insights is checked off; substitutions, adaptation, serving-scale,
  guided cook-mode UI, and general polish are still open.
- **GitHub ticket discipline is now live** (commit `97864c6`, issue
  [#6](https://github.com/crason-t/Pantry/issues/6), closed): one milestone
  per remaining feature area — substitutions
  ([#1](https://github.com/crason-t/Pantry/milestone/1)), adaptations
  ([#2](https://github.com/crason-t/Pantry/milestone/2)), serving-scale
  ([#3](https://github.com/crason-t/Pantry/milestone/3)), cook mode
  ([#4](https://github.com/crason-t/Pantry/milestone/4)), polish
  ([#5](https://github.com/crason-t/Pantry/milestone/5)) — plus a
  `.githooks/commit-msg` hook (wired via `git config core.hooksPath
  .githooks`) that **rejects any commit whose message doesn't reference an
  issue number**, and workflows that tag/release on milestone close and
  nag un-milestoned issues. This affects every commit from here forward,
  including the work below: it landed as commit `5bfec2d` ("Add username
  login, persistent nav, and form styling pass (#7)"), issue
  [#7](https://github.com/crason-t/Pantry/issues/7) still open (the commit
  references it but the issue itself hasn't been closed).
- Nav/auth/styling work from `5bfec2d`, **committed and pushed**:
  - Shared `Layout`/nav component (`frontend/src/components/Layout.tsx`),
    wired into `ProtectedRoute` — persistent top bar (brand link, "Cookbook"
    nav link with active-state underline, "+ New recipe", user email,
    "Log out") now appears on every authed page. Fixes the earlier gap where
    leaving the cookbook left no way back except browser history.
  - Global button/input/textarea/select styling in `frontend/src/index.css`
    (`.btn-primary` / `.btn-secondary` / `.btn-ghost`, focus-visible states,
    disabled states) plus form-centering and radio-group layout fixes in
    `frontend/src/App.css`. Replaces raw browser-default form controls
    (e.g. the Ingest page radios/input were unstyled and mis-centered).
  - Username auth: `User` now has a separate, required, unique `username`
    column alongside `email` (migration
    `backend/alembic/versions/fe8609b4be38_add_username_to_users.py`,
    applied). Login accepts either as the identifier
    (`backend/app/api/routes/auth.py`, `frontend/src/pages/LoginPage.tsx`);
    registration now collects both (`frontend/src/pages/RegisterPage.tsx`).
  - Test fixture account for ongoing dev/test use: email `test@mail.com`,
    username `a`, password `password` — created via direct API calls, not
    through the UI.
  - Seeded that test account's cookbook with two recipes: a simple pasted-
    text one ("Garlic Butter Toast") and a real showcase recipe pulled live
    from the web ("Red Wine Braised Short Ribs",
    onceuponachef.com/recipes/red-wine-braised-short-ribs.html) chosen
    because it generates insights spanning all 3 glossary categories
    (maillard_reaction, emulsification, umami, acidity, deglaze, braise) —
    not just Maillard.
- **Three parallel-agent PRs delivered, all draft/unreviewed/unmerged:**
  - [PR #9](https://github.com/crason-t/Pantry/pull/9) — cookbook list
    redesigned from a bare `<li>` list to a responsive card grid
    (`RecipeCard.tsx`); closes the highest-leverage visual gap noted below
    previously. References issue #5 (Polish).
  - [PR #10](https://github.com/crason-t/Pantry/pull/10) — on-demand
    ingredient-substitution suggestions (issue
    [#1](https://github.com/crason-t/Pantry/issues/1)): new
    `POST /recipes/{id}/ingredients/{id}/substitutions` route
    (`services/substitutions.py`, Claude structured output), click-to-expand
    `SubstitutionPanel` on the recipe detail page. Nothing persisted, per
    `docs/MVP.md`.
  - [PR #11](https://github.com/crason-t/Pantry/pull/11) — per-user
    ingredient customization (issue
    [#8](https://github.com/crason-t/Pantry/issues/8)): new
    `IngredientCustomization` table scoped to `SavedRecipe` (migration
    `f53637646efe`) so edits never mutate the shared `Ingredient` rows other
    users' saved copies of the same recipe point at; merge-at-read-time
    service layer; "Edit ingredients" toggle on the recipe detail page.
    Deliberately left `IngredientRow`'s internals untouched to minimize
    collision with PR #10 — **both PRs touch `RecipeDetailPage.tsx`, so
    expect a rebase/merge-order decision between them.**
  - None of the three have had a human browser click-through yet (PR #10 was
    E2E-tested against real Postgres with Claude mocked; PR #11's migration
    was verified up/down/up against Postgres; PR #9's build/lint passed) —
    manual verification is still outstanding before merge.
- **Scope creep caught and corrected mid-session:** the PR #11 agent kept
  acting after its assigned task was done — stood up ad hoc dev servers
  (backend `:8001` ×2, frontend `:5175`) against the shared local Postgres
  with an uncommitted local-only CORS tweak
  (`backend/app/main.py`, adds `localhost:5175` to `allow_origins`), and
  unilaterally filed issue #16 (see below). Reviewed with Carson: the
  servers stay running for now (his call), the CORS tweak stays
  **uncommitted** (it's a debugging convenience for that ad hoc setup, not
  part of the feature — don't ship it in PR #11), and issue #16 stays open.
  No standing change made to how agents operate — treated as a one-off.
- Known, not-yet-fixed gaps (still open, now tracked as GitHub issues):
  - No 404/catch-all route — an unmatched path just renders blank (React
    Router logs a console warning only, nothing shown to the user). Not
    yet filed.
  - `CookModePage` is an intentional placeholder ("guided step-by-step...
    lands later"), not a bug — tracked as issue
    [#4](https://github.com/crason-t/Pantry/issues/4).
  - Recipes ingested via URL where the page has schema.org JSON-LD never
    get `quantity`/`unit`/`colloquial_quantity`/`component` split out —
    tracked as issue
    [#16](https://github.com/crason-t/Pantry/issues/16) (see scope-creep
    note above for how this one got filed).
  - The experimental Steps List/Cards toggle (`RecipeDetailPage.tsx`,
    `StepCard.tsx`) is still being evaluated by the user ("not sure if
    I'll actually like it") — no decision yet on keep/iterate/drop.
    Defaults to List and has no persistence, so trying it costs nothing.
- Additional issues opened (outside this conversation) since the last
  entry: [#12](https://github.com/crason-t/Pantry/issues/12) Claude Code
  subagents for Pantry dev workflows, [#13](https://github.com/crason-t/Pantry/issues/13)
  graphic-design skill for one-off visual assets, [#17](https://github.com/crason-t/Pantry/issues/17)
  internal ticket-tracking UI ("Jira-lite", milestone "Ticket tracker",
  draft [PR #18](https://github.com/crason-t/Pantry/pull/18)), and
  [#19](https://github.com/crason-t/Pantry/issues/19) seed a persistent test
  account. **New this session:**
  [#23](https://github.com/crason-t/Pantry/issues/23) extend the
  `save-progress` skill (below) — closed out this session.
- **The `save-progress` skill** (`.claude/skills/save-progress/SKILL.md`)
  was extended to match NeeDoh's version: commits/pushes outstanding work
  with issue references, proposes (doesn't auto-close) ticket-reconciliation
  candidates, flags drift against `CLAUDE.md`/`docs/MVP.md`, and — new,
  specific to Pantry — checks every worktree under `pantry-worktrees/*` and
  `.claude/worktrees/*`, not just the main checkout, since parallel-agent
  work regularly lands there. Issue #23, committed this session.
- `.claude/worktrees/` holds other sessions' locked worktrees (currently
  `quizzical-dazzling-leaf`, `scrollable-cards`, `ticket-tracker`) — left
  untouched, not attributable to this session.
- Update: the `ticket-tracker/` directory mentioned in an earlier version
  of this note is no longer just sitting untracked in the main checkout —
  it's now committed on branch `standalone-ticket-tracker`, pushed, and
  open as draft PR #24 (see the History entry below for the full story,
  including why it superseded PR #18 and two real collisions that came
  from building it directly in the shared main checkout).
- Untracked, pre-existing, unrelated to this session: `get-docker.sh` (the
  official Docker install script, likely a leftover from setting up Docker
  Desktop) — probably safe to delete or `.gitignore`, but not touched.
- `CLAUDE.md`'s "Project status" section still says the repo is
  pre-scaffolding with no backend/frontend — badly stale, flagged rather
  than silently edited (see "Flag drift" in the save-progress skill).

## In progress / blockers

- **PRs #9, #10, #11 open and draft, blocked on human review/merge** — none
  have had a manual browser click-through. #10 and #11 both touch
  `RecipeDetailPage.tsx`; merge one first and rebase the other rather than
  merging both blind.
- Two ad hoc dev servers still running by Carson's choice: backend `:8001`
  (×2 processes) and frontend `:5175`, rooted in the
  `pantry-worktrees/recipe-customization` worktree, against the shared
  local Postgres. Not blocking anything, just worth knowing they're live.
- Otherwise nothing blocking — all code work through this session's
  commits is committed and pushed.

## Next steps

Per Carson's standing note in `CLAUDE.md` (flagged at the top of every
session until acted on):
1. A recipe-ingestion bug: ingested ingredient names sometimes include
   their measurement text duplicated in the name itself. Needs a screenshot
   from Carson of the ingredients table to diagnose.
2. Save progress + push all outstanding changes — done as of this entry.
3. Redesign the Cookbook tab (currently a bare list, "thrown together") —
   **done this session, see PR #9 above; still needs review/merge.**
4. Set up a design system using Claude Design (Figma).
5. Finish the Jira-lite ticket-tracking UI and hook it up to the project
   structure — tracked as issue #17. **Done this session as a standalone
   app, see PR #24 above; supersedes PR #18. Needs review/merge, and a
   call on whether to close #18.**
6. Build a skill to spin up named local dev instances (reserved ports,
   descriptive browser-tab titles per feature under test) plus a page to
   navigate between them.

Also still open:
- Review and merge PRs #9, #10, #11 (watch the #10/#11 rebase on
  `RecipeDetailPage.tsx`); tear down the ad hoc `:8001`/`:5175` servers
  once #11 is merged and no longer needed.
- Review and merge PR #24 (standalone ticket tracker); decide whether to
  close superseded PR #18. To run PR #24 locally: check out
  `standalone-ticket-tracker` **in a worktree, not the main checkout** —
  see the collision notes in this entry's "Did" section for why.
- Add a 404/catch-all route with a real "page not found" message.
- Continue `docs/PROJECT_PLAN.md`'s remaining build-sequence items:
  adaptation endpoint+UI, serving-scale endpoint+UI, guided cook-mode UI,
  broader loading/error-state polish.
- Decide on the JSON-LD quantity-splitting gap (issue #16).
- Get a read on the Steps Cards view before investing further in it.
- `CLAUDE.md`'s "Project status" section is stale (says pre-scaffolding) —
  worth a fix next time that file is touched.

---

## History

### 2026-07-29
**Did:**
- Added a shared `Layout` nav component (brand, "Cookbook" link w/ active
  state, "+ New recipe", user email, "Log out"), wired into `ProtectedRoute`
  so it wraps every authed page; removed the now-redundant logout/ingest-link
  bits from `CookbookPage`.
- Added global `button`/`input`/`textarea`/`select` styles to `index.css`
  (`.btn-primary`/`.btn-secondary`/`.btn-ghost`, focus-visible, disabled) and
  fixed the Ingest page's uncentered form + cramped radio group in `App.css`.
- Added a separate `username` column on `User` (migration
  `fe8609b4be38`, backfilled existing rows from email local-part), made
  login accept email-or-username, and added the username field to
  registration (backend `auth.py`/`schemas/user.py`/`models/user.py`;
  frontend `LoginPage`/`RegisterPage`/`AuthContext`/`api/types.ts`).
- Created a `test@mail.com` / username `a` / password `password` test
  account via direct backend API calls, and seeded its cookbook with two
  saved recipes (one pasted-text, one ingested live from a real URL chosen
  specifically for insight-category variety).
- Reviewed the app in Chrome throughout (Cookbook, Ingest, Recipe Detail,
  Cook Mode, Login) to identify UI gaps: bare unstyled form controls, no
  persistent nav, no card grid on the cookbook list, no 404 handling.
- Committed and pushed the above as `5bfec2d` (#7), plus GitHub ticket
  discipline itself landed as `97864c6` (#6, closed) — one milestone per
  remaining feature area with a `commit-msg` hook enforcing an issue
  reference on every commit. Carson also opened follow-on issues #8
  (editable ingredients), #12 (Pantry dev-workflow subagents), #13
  (graphic-design skill), #16 (JSON-LD quantity-splitting gap), and #17
  (Jira-lite ticket-tracking UI). Reconciled `SESSION_LOG.md` and
  `docs/PROJECT_PLAN.md` afterward (this entry) to match actual git/issue
  state — this had drifted since the log was written mid-session, before
  the commit and before the new issues existed.
- Added a standing note at the top of `CLAUDE.md` from Carson: a punch
  list to surface at the start of every session until acted on (recipe-
  ingestion ingredient-name bug w/ screenshot pending, save-progress +
  push [done as of this entry], Cookbook tab redesign, a Claude-Design
  design system, finishing the Jira-lite UI, and a skill to spin up named
  local dev instances with per-feature browser-tab titles).
- (Later the same day, separate conversation.) Dispatched three literal
  parallel background agents, each in its own git worktree against
  `origin/master`, to build the cookbook redesign plus two features Carson
  asked for: PR #9 (cookbook card grid, issue #5), PR #10 (on-demand
  ingredient substitutions, issue #1), PR #11 (per-user ingredient
  customization via a new `IngredientCustomization` overlay table, issue
  #8 — designed specifically so edits never touch the shared `Ingredient`
  rows other users' saved copies point at). Opened issue #8 (with the
  shared-row constraint spelled out) and milestone "Recipe customization"
  before dispatching, per ticket discipline. Also found and committed
  pre-existing uncommitted WIP from an earlier session (username login +
  nav + form styling) as commit `5bfec2d` — see issue #7.
- Caught the PR #11 agent continuing to act after its task was done (ad
  hoc test servers on `:8001`/`:5175` against shared Postgres, an
  uncommitted CORS tweak, and unilaterally filing issue #16) — flagged it
  rather than silently allowing or silently cleaning it up; reviewed with
  Carson, who chose to leave the servers running and keep issue #16 open,
  with no standing process change.
- Extended `.claude/skills/save-progress/SKILL.md` (issue #23) to match
  NeeDoh's version — commit/push with issue refs, propose-not-auto-close
  ticket reconciliation, drift-flagging — plus Pantry-specific
  multi-worktree awareness, then ran it (this entry).
- Carson flagged that the Jira-lite ticket tracker (issue #17) needs to
  live independently of the Pantry app. A concurrent worktree session had
  already built it (branch `worktree-ticket-tracker`, commit `717de1e`,
  never merged to master) but wired it directly into Pantry's own FastAPI
  backend (`backend/app/models/ticket.py`, `backend/app/api/routes/
  tickets.py`) and React frontend, sharing Pantry's DB, auth, and bundle —
  the opposite of independent. Salvaged that work into a new top-level
  `ticket-tracker/` app instead: own FastAPI backend (`ticket-tracker/
  backend`, port 8010), own Vite/React/TS frontend (`ticket-tracker/
  frontend`, port 5180), own Postgres via its own `docker-compose.yml`
  (port 5433, separate container/volume from Pantry's DB). Still lives in
  this same git repo (Carson's choice: standalone app, same repo, not a
  separate repo). Epic/Ticket/TicketComment/TicketActivity models, kanban
  board with drag-and-drop status changes, ticket detail with comments and
  an auto-logged activity feed, and a per-epic progress dashboard — all
  ported from the worktree branch's implementation. Verified end-to-end:
  `alembic upgrade head` applied cleanly, full curl-driven CRUD flow
  (create epic → create ticket → patch status/assignee → add comment →
  fetch with nested comments/activity → list epics with progress), `npm
  run build` clean, and confirmed in an actual browser (kanban board,
  ticket detail page, epics page all render and work).
- Pushed the standalone tracker as branch `standalone-ticket-tracker`
  (commits `d9dd9cf`, `d88a416`) and opened draft
  [PR #24](https://github.com/crason-t/Pantry/pull/24) against it,
  referencing issue #17. Flagged to Carson that this supersedes draft
  [PR #18](https://github.com/crason-t/Pantry/pull/18) (the old,
  non-independent version, still open) — his call whether to close #18.
- Caught two real collisions from running this feature branch directly in
  the **main checkout** (`/Users/carson/Claude/Projects/Pantry`) instead
  of an isolated worktree, both stemming from the fact that this directory
  is being actively shared by multiple concurrent Claude Code sessions
  right now (confirmed via `lsof` — several `claude.exe`/node processes
  with it open):
  1. My `ticket-tracker/docker-compose.yml` defaulted its Compose project
     name to the directory basename `ticket-tracker`, which collided with
     the *unrelated* `.claude/worktrees/ticket-tracker` worktree's own
     `docker-compose.yml` (different DB, same default container name
     `ticket-tracker-db-1`, same host port 5433) — whichever ran `docker
     compose up` most recently silently stole the other's container and
     broke its DB connection. Fixed (commit `d88a416`): pinned an explicit
     `name: pantry-standalone-ticket-tracker` and moved the host port to
     5434.
  2. Twice during this session, another concurrent session running in this
     same main checkout ran `git checkout` and switched the shared working
     tree to a different branch (once to `master`) out from under this
     one — since `ticket-tracker/` only exists as tracked files on the
     `standalone-ticket-tracker` branch, each switch deleted the directory
     off disk and broke the locally running dev servers (backend `:8010`,
     frontend `:5180`). Not recoverable by just switching back once it's
     someone else's turn to use the checkout — killed the orphaned
     processes rather than fight over the shared branch state.
  **Takeaway for future sessions:** don't build or run feature-branch work
  directly in the main checkout — use `EnterWorktree` (or `pantry-
  worktrees/*` / `.claude/worktrees/*` by hand) for anything that needs
  its own branch and its own live dev servers, exactly like the other
  concurrent sessions' work in this same log already does. The main
  checkout should be treated as shared/transient, not a safe place to run
  a long-lived local server from.

**Decisions:**
- Dropped auth entirely for the ticket tracker rather than reimplementing
  Pantry's JWT system independently: it's a single-user local dev tool, so
  `reporter`/`assignee`/`author`/`actor` are plain strings defaulting to
  `"carson"` instead of foreign keys to a `User` table. No login screen.
- Kept it in the Pantry repo as a sibling top-level directory rather than a
  separate git repo, per Carson's explicit choice — full separation of
  backend/frontend/database/ports, but shared version control.
- Picked ports 8010 (backend) and 5180 (frontend) specifically to avoid
  colliding with Pantry's own 8000/5173, given how many worktrees/dev
  servers tend to be running at once (see punch-list item 6 above).
- Button/input styling uses bare-element selectors (`button`, `input`, etc.)
  as an automatic baseline so any future form/control gets sane styling for
  free, plus explicit `.btn-*` classes for anchors styled as buttons and for
  signaling primary/secondary/ghost intent explicitly rather than inferring
  it from `type="submit"`.
- Added a dedicated `--accent-contrast` CSS variable (white in light mode,
  near-black in dark mode) instead of hardcoding white button text — the
  dark-mode accent purple (`#c084fc`) fails contrast against white
  (~2.6:1) but passes well against dark text (~7.5:1).
- Username was made a required, separate, unique field (not just an email
  alias) per explicit user request, with login matching
  `email == identifier OR username == identifier`.
- The showcase recipe was sourced via a live web search rather than reused
  from the existing demo recipes, per explicit instruction not to pull from
  a fixed list, and picked specifically because it exercises 6 of the 8
  seeded glossary terms across all 3 categories (reaction/flavor/technique)
  in one recipe.

**Next:** review/merge PR #24 (standalone ticket tracker) and decide on
superseded PR #18; otherwise wait for Carson's direction on the rest of
the punch list — offered the cookbook redesign, design system, and
Jira-lite UI as options earlier and he said "Done for now" without
picking one, then came back and asked specifically for the ticket
tracker to be independent (done, see above).

**Open questions / blockers:** the ingredient-name/measurement ingestion
bug (item 1) is still waiting on a screenshot from Carson; whether to
close PR #18 now that PR #24 supersedes it.

(Reconciliation commit `f6bfb24` also landed this same day, syncing this
log and `docs/PROJECT_PLAN.md` with git/issue state that had drifted —
see the "Current State" section above.)

### 2026-07-28
**Did:**
- Redesigned the recipe detail page's ingredient/step display away from
  raw bullet lists to clean grouped rows: ingredients can be grouped under
  a `component` sub-heading (e.g. "Dressing"), and each row shows a natural
  colloquial quantity ("a spoonful", "1 head") as the bold primary amount
  with the precise weight as a secondary line when both exist. Added
  `component` and `colloquial_quantity` columns to `Ingredient`
  (`backend/app/models/ingredient.py`) and updated the Claude extraction
  prompt (`backend/app/services/ingestion/claude_extractor.py`) to
  populate them.
- Added a `RecipeTip` model (`backend/app/models/recipe_tip.py`) generated
  alongside insights at ingestion time, rendered as a "Tips" list above
  Ingredients. Restyled the general "why this dish works" insights into a
  card grid (`InsightCard.tsx`) and tightened the generation prompt
  (`backend/app/services/insights.py`) to surface only the 2-4 truly
  major, dish-defining aspects (can call out common mistakes) instead of
  any dish-wide observation.
- Added an experimental List/Cards toggle for Steps
  (`RecipeDetailPage.tsx`): Cards view flips each step (`StepCard.tsx`) to
  reveal its tip on the back; a "Keys of the recipe" summary compiles
  every step tip in one place and shows regardless of which Steps view is
  active — only the List vs. Cards steps display itself changes. Defaults
  to List, resets on reload — a no-cost, fully reversible experiment per
  explicit user request ("make it easily reversible").
- Diagnosed (didn't fix) why ingredients appeared to "disappear" for two
  real cookbook recipes (ids 9, 10): confirmed via direct DB query that no
  data was lost — it's the pre-existing JSON-LD ingestion gap described
  above, just made more visible by the new row layout.
- Committed and pushed all of the above in three commits (`3be9631`,
  `7ea5fae`, `964c6b2`).
- Noted (via `ps`, not assumption, per feedback below) that the `claude`
  CLI process itself spawns `caffeinate -i -t 300` as a direct child to
  keep macOS from sleeping — not something invoked through any tool call
  in this conversation.
- Saved a feedback memory (`feedback-verify-before-answering`) after
  answering the caffeinate question wrong from assumption on the first
  try: verify actual state (`ps`, files, git, API responses) before
  answering rather than reasoning from general knowledge, whenever a cheap
  check is available.
- Picked up a `97864c6` commit made outside this conversation (GitHub
  ticket discipline: milestones #1-5, issue #6 closed, commit-msg hook
  requiring an issue reference, milestone-release/require-milestone
  workflows) and folded it into Current State above — most relevant part:
  issue #7 already tracks the uncommitted username/nav-shell work noted in
  the entry above this one, so it's not an orphaned blocker.

**Decisions:**
- Kept tips + insights generation as a single Claude call (extended the
  existing `GeneratedInsights` schema with a `tips` field) rather than a
  second call, to avoid adding ingestion latency/cost.
- Left `jsonld_parser.py` untouched rather than guessing a fix when asked
  why ingredients seemed to disappear — explained the root cause via a DB
  check and left the fix decision to the user.

**Next:** decide whether to close the JSON-LD quantity-splitting gap; get
a read on the Steps Cards view; otherwise continue the remaining
`docs/PROJECT_PLAN.md` build-sequence items.

**Open questions / blockers:** whether to extend `jsonld_parser.py` for
quantity/unit splitting; whether the user keeps the Steps Cards view.
