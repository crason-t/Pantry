# Pantry — MVP Spec

## Vision

Long-term, Pantry is a home pantry/inventory + recipe + grocery-budget
assistant. This repo currently scopes only the **recipe-assistant MVP**
described below; pantry inventory tracking and grocery budgeting are future
work, not part of this build.

## MVP Features

1. **Ingest** a recipe via URL or pasted raw text.
2. **Structured reformat** — title, servings, prep/cook/total time,
   ingredients (with quantities), ordered steps, equipment — into an easily
   scannable layout.
3. **"Why this dish works"** — a culinary insight explaining what makes the
   dish taste the way it does (technique, flavor pairing, etc.), generated
   once at ingestion time.
4. **Ingredient substitutions** — on-demand suggestions for ingredients the
   user might not have.
5. **Adaptation** for a different cooking method or equipment (e.g. different
   pan, no stand mixer, oven vs. stovetop).
6. **Scaling** for a different number of servings/volume.
7. **Guided step-by-step cook mode** — simple tap next/back UI, one step at a
   time. Explicitly **not** voice/hands-free for MVP.
8. **Cookbook** — save ingested recipes to a personal collection tied to the
   user's account.

## Explicit Non-Goals (MVP)

- Pantry inventory tracking
- Grocery budget / spend tracking
- Voice or hands-free cook mode
- Multi-tenant / recipe sharing across users
- Mobile app (planned for later, but not part of this build — the backend API
  is kept clean and reusable so a future React Native app can call it)

## Architecture Decisions

| Decision | Choice | Why |
|---|---|---|
| Backend | FastAPI (Python) | Async-friendly for LLM calls + URL fetches; Pydantic validation pairs naturally with Claude's structured-output schemas |
| Frontend | Vite + React + TypeScript, plain SPA | App lives entirely behind login — no SSR/SEO need; keeps a clean API boundary a future mobile app can reuse |
| Database | PostgreSQL via Docker Compose | Trivial to run locally; JSONB for flexible fields; avoids a migration the moment this becomes multi-user |
| Auth | Rolled JWT auth (passlib + python-jose + OAuth2PasswordBearer) | Wanted real login built now; rolling it is ~half a day and keeps everything transparent, no external account/dependency |
| LLM | Anthropic Claude API, `anthropic` Python SDK, default model `claude-opus-5` (configurable via `CLAUDE_MODEL`) | Structured outputs (`output_config.format`) fit recipe parsing well |

These are defaults, not locked in — revisit if e.g. SQLite (simpler, single-user)
or a hosted auth provider (Clerk, faster + built-in RN SDK) turn out to fit
better once mobile is in scope.

## Data Model Summary

- **User** — id, email (unique), hashed_password, created_at
- **Recipe** — id, title, servings, prep_time, cook_time, total_time,
  equipment (JSON list), source_url (nullable), raw_source_text (nullable),
  created_by_user_id (FK), why_it_works (text, nullable — cached insight),
  created_at
- **Ingredient** — id, recipe_id (FK), position, quantity, unit, name, notes
  (nullable), raw_text
- **Step** — id, recipe_id (FK), position, instruction (text)
- **SavedRecipe** (cookbook entry) — id, user_id (FK), recipe_id (FK),
  saved_at, unique(user_id, recipe_id)

Ingredients and steps are child rows (not JSON blobs) so scaling and the
scannable-structure view can operate on typed data. Substitutions and
adaptations are **not persisted** for MVP — computed on demand via Claude each
time; add caching later only if latency/cost becomes a real problem.

## Recipe Ingestion Architecture

```
services/ingestion/
├── url_fetcher.py      # httpx GET with timeout + UA header → raw HTML
├── jsonld_parser.py    # scan <script type="application/ld+json"> for
│                       # schema.org Recipe data — no LLM needed when present
├── claude_extractor.py # Claude call (output_config.format / json_schema) to
│                       # extract a ParsedRecipe when JSON-LD is absent or
│                       # incomplete; also the only path for pasted raw text
└── pipeline.py         # ingest_from_url(url): fetch → try jsonld → fallback
                         # ingest_from_text(text): always goes through Claude
```

Both paths converge on one internal `ParsedRecipe` Pydantic schema before
persistence, so downstream logic never needs to know which path produced the
data.
