# Pantry — Session Log

## Current State (as of 2026-07-29)

- Backend + frontend are fully scaffolded and working end-to-end (FastAPI +
  Postgres, Vite/React/TS SPA): auth, recipe ingestion (URL or pasted text,
  via Claude), "Keys of the recipe" / "Why this dish works" insights, recipe
  tips, cookbook save/list. See `docs/PROJECT_PLAN.md`'s build-sequence
  checklist for the authoritative status — everything through "Why this
  works" insights is checked off; substitutions, adaptation, serving-scale,
  guided cook-mode UI, and general polish are still open.
- This session's changes, **uncommitted**:
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
- Known, not-yet-fixed gaps (still open):
  - Cookbook list is still a bare `<li>` list, no card grid — the highest-
    leverage remaining visual gap since it's the landing page.
  - No 404/catch-all route — an unmatched path just renders blank (React
    Router logs a console warning only, nothing shown to the user).
  - `CookModePage` is an intentional placeholder ("guided step-by-step...
    lands later"), not a bug — last item in the build sequence.
  - Recipes ingested via URL where the page has schema.org JSON-LD
    (`backend/app/services/ingestion/jsonld_parser.py`) never get
    `quantity`/`unit`/`colloquial_quantity`/`component` split out — that
    parser has always just dumped the whole ingredient line into `name`
    and `raw_text`. The ingredient-row layout only shows a right-side
    quantity badge when those fields are populated, so JSON-LD-ingested
    recipes (locally, ids 9, 10) show rows with nothing on the right —
    not data loss, just a rendering gap the redesign made more visible
    than the old single-bullet layout did.
  - The experimental Steps List/Cards toggle (`RecipeDetailPage.tsx`,
    `StepCard.tsx`) is still being evaluated by the user ("not sure if
    I'll actually like it") — no decision yet on keep/iterate/drop.
    Defaults to List and has no persistence, so trying it costs nothing.
- Untracked, pre-existing, unrelated to this session: `get-docker.sh` (the
  official Docker install script, likely a leftover from setting up Docker
  Desktop) — probably safe to delete or `.gitignore`, but not touched.

## In progress / blockers

- Nothing blocking. This session's diff (backend username-auth + frontend
  nav/styling/username UI) is uncommitted and ready for review/commit.

## Next steps

- Commit this session's work (consider splitting backend auth changes from
  frontend nav/styling, or one combined commit — whichever the user prefers).
- Redesign the Cookbook list as a card grid.
- Add a 404/catch-all route with a real "page not found" message.
- Continue `docs/PROJECT_PLAN.md`'s remaining build-sequence items:
  substitutions endpoint+UI, adaptation endpoint+UI, serving-scale
  endpoint+UI, guided cook-mode UI, broader loading/error-state polish.
- Decide on the JSON-LD quantity-splitting gap (teach `jsonld_parser.py` a
  lightweight split, or leave as a known asymmetry vs. Claude-extracted
  recipes).
- Get a read on the Steps Cards view before investing further in it.
- Noted but explicitly deferred by the user: post-import recipe
  customization (per-ingredient quantity edits, scale-by-pinning-one-
  ingredient rather than a flat serving multiplier, later substitution) —
  see memory `planned-recipe-customization`.

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

**Next:** commit this session's diff; redesign the cookbook list as a card
grid; add a 404 route; resume the remaining `docs/PROJECT_PLAN.md` build-
sequence items (substitutions, adaptation, scaling, cook-mode UI, polish).

**Open questions / blockers:** none.

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
