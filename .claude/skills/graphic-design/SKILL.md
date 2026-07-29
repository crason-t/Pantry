---
name: graphic-design
description: Use this when the user wants a one-off visual asset for Pantry — a logo, favicon, app icon, empty-state illustration, or similar graphic (e.g. "design a logo", "we need a favicon", "make an illustration for the empty cookbook state"). Drafts the asset as SVG, previews it as an Artifact for iteration, then saves the approved file into the frontend and wires it up. Not for syncing a component/design-token library to claude.ai/design — that's a different job and this repo has no skill for it yet.
---

# Graphic Design

Produce a single visual asset for Pantry (logo, favicon, icon, empty-state or
error-state illustration, share/OG image, etc.) and land it in the frontend.

This is deliberately **not** the claude.ai/design "design system" sync flow —
the `DesignSync` tool that backs that is built for pushing a component/token
library to a design-system project, and would need its own skill if Pantry
ever wants that. This skill produces a standalone graphic asset instead,
using SVG + Artifact previews, since that's a much better fit for a single
piece of art in a Vite/React SPA (small, scalable, no build step, easy to
inline or drop in `public/`).

## Steps

1. **Clarify the brief** — before drawing anything, pin down:
   - What the asset is and where it's used (browser tab favicon, header
     logo, an empty-state graphic on a specific page, etc.)
   - Size/aspect constraints (a favicon needs to read at 16–32px; a header
     logo needs to work at whatever height the nav uses; an illustration
     needs to fit its container without a fixed pixel size)
   - Style direction, if the user has one in mind — otherwise propose
     something and let the first draft carry the pitch
   - If light/dark handling matters (it usually does — see below)

   Don't guess silently on anything that meaningfully changes the output;
   ask if it's ambiguous.

2. **Pull the actual brand tokens before drawing** — don't invent a palette.
   Read `frontend/src/index.css` for the live `:root` custom properties
   (`--accent`, `--text`, `--bg`, `--border`, etc.) and their
   `@media (prefers-color-scheme: dark)` overrides. As of this writing the
   accent is a purple (`#aa3bff` light / check the dark block for its
   override) — but re-read the file each time rather than trusting this
   note, since it will drift.

3. **Load `artifact-design`** (the Skill tool) before drafting — it has the
   composition/spacing/hierarchy fundamentals that keep a first-pass SVG
   from looking like a placeholder. If the asset encodes any data (a chart-
   like icon, a progress/stat graphic), load `dataviz` too for the color
   and mark-choice rules.

4. **Draft as SVG**, hand-authored or generated inline — not a raster
   format. Reasons: scales cleanly at any size, tiny file size, can be
   inlined as a React component if it needs to react to theme/state, and
   matches how `frontend/public/favicon.svg` already works in this repo.
   - Use `currentColor` or the CSS custom properties above (via a wrapping
     `<style>` block with `@media (prefers-color-scheme: dark)`) rather than
     hardcoded hex, so the asset survives the app's theme switch for free.
   - Keep the viewBox square/simple unless the use case demands otherwise.

5. **Preview with the Artifact tool**, not a raw file dump — wrap the SVG in
   a minimal HTML page so the user can actually see it (ideally at a few
   scales side by side: e.g. 16px/32px/128px for a favicon, so tiny-size
   legibility is checked, not just the big version). Load `artifact-design`
   guidance covers the light/dark and responsive requirements for the
   wrapper page itself.

6. **Iterate from feedback** — redeploy the same Artifact path (per the
   Artifact tool's update flow) rather than creating a new one each round,
   so the user keeps one stable link across revisions.

7. **Once approved, land the file in the frontend**:
   - Favicon → `frontend/public/favicon.svg` (already exists; overwrite),
     and confirm `frontend/index.html` still references it correctly.
   - Logo/icon used in a component → save under `frontend/src/assets/`
     (create the directory if it doesn't exist yet) and wire the import
     into whatever component needs it (e.g. `Layout.tsx` for a header
     logo).
   - Illustration tied to one page → colocate near that page's component,
     or `frontend/src/assets/` if it's shared.
   Confirm the reference actually resolves — don't just drop the file and
   assume the import path is right.

8. **Respect this repo's ticket discipline** (see root `CLAUDE.md`): if this
   asset is real, non-trivial work (not a tiny tweak), check whether it
   belongs under an existing GitHub milestone/issue before committing, and
   reference that issue number in the commit message — the repo's
   commit-msg hook rejects commits that don't.

## What this skill is not for

- Syncing a reusable component/design-token library to a claude.ai/design
  *design-system* project — that's the `DesignSync` tool's actual job, and
  needs its own skill (likely named `design-sync`) if Pantry ever wants a
  synced component library. Don't reach for `DesignSync` here; it will
  reject writes to a non-design-system project anyway.
- Raster image generation (photos, complex textures) — out of scope for a
  hand-authored-SVG approach. Flag it to the user if the brief turns out to
  need that instead of vector art.
