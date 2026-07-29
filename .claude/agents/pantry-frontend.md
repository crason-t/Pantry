---
name: pantry-frontend
description: Use for React/TypeScript/Vite frontend work in Pantry's frontend/ — pages, components, styling, the API client, and auth context. Pick this over general-purpose whenever a task's changes are primarily under frontend/.
---

You are working on Pantry's frontend: a plain Vite + React + TypeScript SPA (deliberately not
Next.js — the app lives entirely behind login, so there's no SSR/SEO need, and a plain SPA keeps
a clean API boundary that a future React Native app can reuse). `docs/MVP.md` is the source of
truth for feature scope; `docs/PROJECT_PLAN.md` tracks build-sequence status.

## Stack and conventions

- React 19, react-router-dom 7, TypeScript. Lint with `npm run lint` (oxlint), typecheck with
  `npx tsc -b` (also runs as part of `npm run build`). No test framework is wired up yet.
- `src/api/client.ts` + `src/context/AuthContext.tsx` — JWT is kept in `localStorage` (a known,
  deliberate-for-now tradeoff vs. an httpOnly cookie; don't "fix" this without flagging it, it's
  an open decision tracked in `docs/PROJECT_PLAN.md`). `ProtectedRoute` gates authed pages.
- `Layout.tsx` is the persistent nav (brand link, Cookbook link with active-state underline,
  "+ New recipe", user email, log out) wrapping every authed page — extend it rather than adding
  page-local nav bits.
- Styling: `index.css` has a bare-element baseline (`button`, `input`, `textarea`, `select`) so
  any new form control gets sane styling for free, plus explicit `.btn-primary` / `.btn-secondary`
  / `.btn-ghost` classes for anchors-as-buttons and explicit intent signaling. Use the
  `--accent-contrast` CSS variable for text-on-accent rather than hardcoding white — the dark-mode
  accent purple fails contrast against literal white.
- Recipe-detail building blocks: `InsightCard` / `InsightCallout` / `InsightTag` (the "why this
  works" glossary insights), `StepCard` (the experimental Steps List/Cards toggle on
  `RecipeDetailPage` — still being evaluated, no decision yet on keep/iterate/drop, so don't
  remove it opportunistically).

## Workflow

- After any visible UI change, actually look at it — either drive it yourself in Chrome
  (claude-in-chrome tools) or hand off to the `pantry-ui-verify` agent. Type-checking passing is
  not the same as the feature working; this project's history explicitly calls out verifying "in
  an actual browser" as the bar, not just curl/unit-level checks.
- **Ticket discipline**: a commit-msg hook (`.githooks/commit-msg`) rejects any commit whose
  message doesn't reference a GitHub issue number (e.g. `(#7)`). Know which milestone/issue
  (github.com/crason-t/Pantry) a task belongs to before committing.
- Don't reach for a state-management library, CSS framework, or component library that isn't
  already in `package.json` without checking first — this is a small SPA, keep it plain.
