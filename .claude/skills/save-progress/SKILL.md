---
name: save-progress
description: This skill should be used when the user says "save progress", "wrap up", "wrap up the session", "end of session", "update the session log", or is otherwise finishing a work session on Pantry and wants the next session to pick up with full context. Updates SESSION_LOG.md at the repo root with an overwritten "Current State" snapshot and a prepended dated history entry.
---

# Save Progress

Maintain `SESSION_LOG.md` at the repo root as the continuity mechanism between
sessions on this project. A future session starts with no memory of this
conversation — this file is how it gets oriented in under a minute.

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

## Steps

1. **Reconstruct what happened this session** — don't rely on memory alone:
   - `git status --short` and `git diff` (staged + unstaged) for uncommitted work
   - `git log` for any commits made since the last SESSION_LOG.md entry
   - Scan back through the conversation for decisions made, dead ends hit,
     and anything explicitly deferred or left half-done
2. **Read the existing `SESSION_LOG.md`** (if it exists) to see the current
   "Current State" section and the most recent history entry — avoid
   repeating what's already captured, and check whether an entry for
   today's date already exists.
3. **Check `docs/PROJECT_PLAN.md`** — if a build-sequence checkbox was
   completed, or an "open decision" was resolved or changed this session,
   edit that file directly (check the box / update the table row) rather
   than just mentioning it in the log.
4. **Overwrite the "Current State" section** with an as-of date and terse
   bullets: what's done, what's in progress, what's blocked, what's next.
   This section is a snapshot, not a diff — replace it fully each time.
5. **Prepend a new History entry** directly below the `---` divider (newest
   entry on top). If an entry for today's date already exists from an
   earlier run this session, merge into it instead of creating a second one
   for the same day. Use this shape:

   ```markdown
   ### YYYY-MM-DD
   **Did:** what was actually built/changed/decided, with file paths where useful
   **Decisions:** any non-obvious calls made and why (skip if none)
   **Next:** the concrete next step(s) for the following session
   **Open questions / blockers:** anything unresolved (omit if none)
   ```

6. If `SESSION_LOG.md` doesn't exist yet, create it with this skeleton
   before filling it in:

   ```markdown
   # Pantry — Session Log

   ## Current State (as of YYYY-MM-DD)

   - ...

   ---

   ## History

   ### YYYY-MM-DD
   **Did:** ...
   ```

7. Keep every entry terse — bullets over paragraphs, reference `path:line`
   when pointing at code. Report the file path updated; don't paste the
   full file back to the user unless asked.
