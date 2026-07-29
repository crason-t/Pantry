---
name: save-progress
description: Use at the end of a Pantry working session, or whenever the user says "save progress", "wrap up", "wrap up the session", "end of session", "update the session log", "housekeeping", or is otherwise finishing a work session on Pantry and wants the next session to pick up with full context. Updates SESSION_LOG.md, commits and pushes any outstanding changes — across the main checkout and any agent-spawned worktrees — with correct issue references, reconciles which GitHub issues the session's work actually touched, and flags anything that now contradicts CLAUDE.md or docs/MVP.md. Use proactively near the end of any substantial Pantry session even if the user doesn't name it explicitly.
---

# Save Progress

Run this at the close of a Pantry working session. It has three jobs: update
the session log, get all work committed and pushed cleanly, and reconcile the
GitHub ticket state against what actually happened. Don't skip straight to
`git commit` without doing all three — the point of this skill is that
nothing from the session gets lost or left untracked, not just that the
working tree is clean.

Pantry regularly has work spread across **multiple worktrees** — parallel
agents get dispatched into `pantry-worktrees/*` or `.claude/worktrees/*`, each
on its own branch, often each with its own open draft PR. "The session's
work" means all of that, not just whatever's checked out in the main
directory. Don't let a worktree's uncommitted or unpushed state go unnoticed
just because it isn't the current working directory.

## 1. Take stock before touching anything

- `git worktree list` — enumerate every worktree, not just the main checkout.
- In the main checkout and in each worktree from this session: `git status
  --short` and `git diff` (staged + unstaged) for uncommitted work, plus
  `git log origin/master..HEAD --oneline` for commits made but not pushed.
- `gh pr list --state open --repo crason-t/Pantry` to see what's already out
  for review — don't re-describe an already-open PR as new work, and don't
  push a worktree's branch as a fresh commit if it already has a PR open
  against it.
- Read `SESSION_LOG.md`'s "Current State" section and most recent history
  entry so you know what was true *before* this session, not just what's
  true now.

**Only touch what this session actually did.** Pantry has had draft PRs and
worktrees appear from other sessions (including ones opened by agents acting
outside their assigned scope). If you find uncommitted work, an open PR, or a
running process you can't attribute to this session's conversation, don't
sweep it into this session's commit/push/reconcile pass — flag it and ask
rather than guess at ownership.

Don't guess at what happened this session from the diff alone — if the scope
of the session isn't obvious from the conversation, ask rather than
reconstruct it. A wrong guess here produces a session log that's confidently
wrong, which is worse than no log.

## 2. Update SESSION_LOG.md

Pantry has no dedicated session-logging subagent (unlike NeeDoh's
`session-logger`) — do this step directly.

`SESSION_LOG.md` has two parts:

1. **Current State** — a snapshot overwritten every run. Answers "where do
   things stand right now" without reading any history.
2. **History** — a dated entry prepended (newest first) every run. Answers
   "what happened and why" for anything the snapshot alone can't explain.

Do not confuse this with `docs/PROJECT_PLAN.md`, which already exists as the
build-sequence checklist and open-decisions table. `PROJECT_PLAN.md` is the
roadmap ("what to build, in what order"); `SESSION_LOG.md` is the session
history ("what actually happened, session by session"). Keep them
non-contradictory: if this session completed or changed a `PROJECT_PLAN.md`
checklist item or open decision, update that file too as part of this skill.

- **Overwrite** the "Current State" section with an as-of date and terse
  bullets: what's done, what's in progress (name the branch/PR), what's
  blocked, what's next. This section is a snapshot, not a diff — replace it
  fully each time.
- **Prepend** a new History entry directly below the `---` divider (newest
  entry on top). If an entry for today's date already exists from an earlier
  run this session, merge into it instead of creating a second one for the
  same day. Use this shape:

  ```markdown
  ### YYYY-MM-DD
  **Did:** what was actually built/changed/decided, with file paths where useful
  **Decisions:** any non-obvious calls made and why (skip if none)
  **Next:** the concrete next step(s) for the following session
  **Open questions / blockers:** anything unresolved (omit if none)
  ```

- If `SESSION_LOG.md` doesn't exist yet, create it with this skeleton first:

  ```markdown
  # Pantry — Session Log

  ## Current State (as of YYYY-MM-DD)

  - ...

  ---

  ## History

  ### YYYY-MM-DD
  **Did:** ...
  ```

- Keep every entry terse — bullets over paragraphs, reference `path:line`
  when pointing at code.

## 3. Get every change committed and pushed

Every commit needs an issue reference (`#N`) — the `commit-msg` hook
(`.githooks/commit-msg`, wired via `git config core.hooksPath .githooks`)
enforces this across the main checkout and every worktree alike. For each
logical chunk of uncommitted work, wherever it lives:

- Check whether an existing GitHub issue already covers it: `gh issue list
  --repo crason-t/Pantry --search "<keywords>"`.
- If nothing fits, this is exactly the situation CLAUDE.md's "Ticket
  discipline" section describes: open a new issue under the right milestone
  before committing. Don't commit untracked work against a fabricated or
  unrelated issue number just to satisfy the hook.
- Write commit messages that describe *why*, referencing the issue, e.g.
  `git commit -m "Fix flavor-glossary seed ordering (#12)"`.
- If a worktree's branch already has an open PR, push to that branch — don't
  open a duplicate PR.
- `git push` once everything is committed, in each worktree that has local
  commits. If a push is rejected because it touches `.github/workflows/*`,
  the token needs the `workflow` OAuth scope — tell the user and point them
  at `gh auth refresh -h github.com -s workflow` rather than silently giving
  up or working around it.

## 4. Reconcile ticket state — propose, don't auto-close

Look at which issues this session's commits reference. For each one, check
whether the work looks complete against that issue's acceptance criteria
(the issue body, cross-referenced with `docs/PROJECT_PLAN.md`).

- If a story looks genuinely done, **propose** closing it — name the
  candidates and why — rather than closing it yourself. Whether "done"
  really means done is a judgment call that belongs to the person who asked
  for the work.
- If a milestone would have every issue closed once those candidates are
  closed, say so explicitly — closing the milestone is what triggers the
  automatic release (`.github/workflows/milestone-release.yml`), so it's
  worth surfacing even though closing it isn't your call.

## 5. Flag drift, don't fix it silently

If anything this session did contradicts `CLAUDE.md` or `docs/MVP.md` — a
rule that turned out to be wrong in practice, a decision that supersedes
what's written — say so explicitly. Don't edit those files yourself without
confirming first; surface the contradiction and let the user decide whether
the rule or the code is what should change.

`CLAUDE.md`'s "Project status" section in particular is known to go stale
fast (it currently describes the repo as pre-scaffolding, which is no longer
true) — if you notice it's out of date, flag it rather than silently editing
around it.

## Output

End with a short, scannable summary: what got committed (with issue
numbers, and which worktree/branch), what's still uncommitted and why, which
tickets are close-candidates, and any drift you're flagging. This is the
part the user actually reads — don't pad it with a transcript of every
command you ran.
