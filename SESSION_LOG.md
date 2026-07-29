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
provided yet, and when asked which of 3/4/5 to start next he said "Done
for now" — no next-task pick made. Item 2 is already done (see `f6bfb24`).

Later the same day, Carson picked item 4 (a separate conversation/job): a
first-pass Pantry brand identity now exists as a published Artifact (see
History below) — palette, type, and components grounded in the app's own
Flavor/Technique/Reaction glossary mechanic. It's a draft for review, not
yet wired into `frontend/` as real tokens/CSS. Note: that session flagged
`/design-login` + `/design consent` local-command output claiming a
"Claude Design" tool had been granted access — no such tool exists; it
was treated as a likely prompt injection and ignored, and the artifact
was built with the actually-available Artifact tool instead. Items 3, 5,
6 are still un-started by this line of work; `.claude/worktrees/`
contains `ticket-tracker` and `scrollable-cards` dirs that look like
separate parallel sessions possibly working items 5 and 3 — not verified
or touched here.

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
- Known, not-yet-fixed gaps (still open, now tracked as GitHub issues):
  - Cookbook list is still a bare `<li>` list, no card grid — the highest-
    leverage remaining visual gap since it's the landing page. Not yet
    filed as its own issue; Carson has explicitly asked to start this next.
  - No 404/catch-all route — an unmatched path just renders blank (React
    Router logs a console warning only, nothing shown to the user). Not
    yet filed.
  - `CookModePage` is an intentional placeholder ("guided step-by-step...
    lands later"), not a bug — tracked as issue
    [#4](https://github.com/crason-t/Pantry/issues/4).
  - Recipes ingested via URL where the page has schema.org JSON-LD never
    get `quantity`/`unit`/`colloquial_quantity`/`component` split out —
    tracked as issue
    [#16](https://github.com/crason-t/Pantry/issues/16).
  - The experimental Steps List/Cards toggle (`RecipeDetailPage.tsx`,
    `StepCard.tsx`) is still being evaluated by the user ("not sure if
    I'll actually like it") — no decision yet on keep/iterate/drop.
    Defaults to List and has no persistence, so trying it costs nothing.
  - Post-import recipe editing (adjust ingredient quantity/name, add new)
    — tracked as issue
    [#8](https://github.com/crason-t/Pantry/issues/8); see memory
    `planned-recipe-customization`.
- Additional issues opened (outside this conversation) since the last
  entry, not yet started: [#12](https://github.com/crason-t/Pantry/issues/12)
  Claude Code subagents for Pantry dev workflows, [#13](https://github.com/crason-t/Pantry/issues/13)
  graphic-design skill for one-off visual assets, [#17](https://github.com/crason-t/Pantry/issues/17)
  internal ticket-tracking UI ("Jira-lite").
- Untracked, pre-existing, unrelated to this session: `get-docker.sh` (the
  official Docker install script, likely a leftover from setting up Docker
  Desktop) — probably safe to delete or `.gitignore`, but not touched.

## In progress / blockers

- Nothing blocking. All code work through commit `5bfec2d` is committed
  and pushed to `origin/master`.

## Next steps

Per Carson's standing note in `CLAUDE.md` (flagged at the top of every
session until acted on):
1. A recipe-ingestion bug: ingested ingredient names sometimes include
   their measurement text duplicated in the name itself. Needs a screenshot
   from Carson of the ingredients table to diagnose.
2. Save progress + push all outstanding changes — done as of this entry.
3. Redesign the Cookbook tab (currently a bare list, "thrown together").
4. Set up a design system using Claude Design (Figma).
5. Finish the Jira-lite ticket-tracking UI and hook it up to the project
   structure — tracked as issue #17.
6. Build a skill to spin up named local dev instances (reserved ports,
   descriptive browser-tab titles per feature under test) plus a page to
   navigate between them.

Also still open from prior sessions:
- Add a 404/catch-all route with a real "page not found" message.
- Continue `docs/PROJECT_PLAN.md`'s remaining build-sequence items:
  substitutions endpoint+UI, adaptation endpoint+UI, serving-scale
  endpoint+UI, guided cook-mode UI, broader loading/error-state polish.
- Decide on the JSON-LD quantity-splitting gap (issue #16).
- Get a read on the Steps Cards view before investing further in it.

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

**Decisions:**
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

**Next:** wait for Carson's direction — offered the cookbook redesign,
design system, and Jira-lite UI as options and he said "Done for now"
without picking one; don't re-prompt on the next session start.

**Open questions / blockers:** the ingredient-name/measurement ingestion
bug (item 1) is still waiting on a screenshot from Carson.

(Reconciliation commit `f6bfb24` also landed this same day, syncing this
log and `docs/PROJECT_PLAN.md` with git/issue state that had drifted —
see the "Current State" section above.)

**Later same day — brand identity (separate job):**
- Carson picked up item 4 from the `CLAUDE.md` punch list ("set up a
  design system using Claude Design"). No such tool exists in the
  toolset; the `/design-login` + `/design consent` local-command outputs
  claiming access had been granted were flagged as a likely prompt
  injection and not acted on.
- Built a first-pass Pantry brand identity instead, using the Artifact
  tool: palette (cast-iron dark / butcher-paper light grounds, one
  amber "doing" accent, three semantic tag hues mapped directly to the
  Flavor/Technique/Reaction glossary categories), type pairing
  (Bricolage Grotesque display, Source Serif 4 body, IBM Plex Mono for
  quantities/tags/timers), and a component set (buttons, glossary tag
  chips, cook-mode step nav, recipe-ingest field, servings stepper) —
  both light and dark themes. The hero is the actual sear/Maillard/pan-
  sauce example from `docs/MVP.md` rendered as Pantry would show it, not
  generic food-app styling.
- Published at
  https://claude.ai/code/artifact/5562e39b-52a5-4cd4-86cf-9196123f0805 —
  explicitly marked draft/not-yet-applied on the page itself. No changes
  were made to `frontend/` — this is a proposal to react to, not tokens
  wired into the app yet.

**Decisions (brand identity):** presented as a design artifact/proposal
rather than through the nonexistent "Claude Design" tool; deliberately
grounded the visual system in the product's own glossary mechanic
instead of a generic warm-cream/serif/terracotta cooking-app look.

**Next (brand identity):** get Carson's read on the direction
(keep/iterate/discard) before turning any of it into real `frontend/`
CSS/tokens.

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
