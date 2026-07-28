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
3. **"Why this dish works"** — culinary insight highlighting the important
   things actually happening in the recipe, not just the literal steps. Two
   parts, inspired by cookwell.com's recipe breakdowns:
   - A shared, curated **glossary** of terms in three categories —
     **Flavor** (aroma, taste, texture, sight, physical, human/emotional —
     the elements that make up perceived flavor), **Technique** (bake, sear,
     braise, emulsify by hand, etc. — the methods used to cook), and
     **Reaction** (Maillard reaction, caramelization, gelation, emulsification,
     fermentation, etc. — the food-science mechanism a technique triggers).
     Each term has a fixed, reusable definition, independent of any one
     recipe.
   - Per-recipe **callouts** generated at ingestion time: for the
     ingredients/steps that matter, tag the relevant glossary term(s) and add
     a short recipe-specific note on why it applies *here* (e.g. technique
     `sear` + reaction `maillard_reaction`, note: "this is what builds the
     fond the pan sauce depends on"). Callouts are anchored inline to a
     specific step/ingredient where possible, and surfaced in both the
     scannable layout and cook mode — not dumped as one paragraph.
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
  created_by_user_id (FK), created_at
- **Ingredient** — id, recipe_id (FK), position, quantity, unit, name, notes
  (nullable), raw_text
- **Step** — id, recipe_id (FK), position, instruction (text)
- **GlossaryTerm** — id, category (enum: flavor | technique | reaction), slug
  (unique, e.g. `maillard_reaction`), name, definition (text). Shared
  reference data, not tied to any one recipe — seeded/curated up front (the
  domain is finite and well-known: a fixed list of techniques, reactions, and
  flavor elements), not generated per ingestion.
- **RecipeInsight** ("why this dish works" callouts) — id, recipe_id (FK),
  glossary_term_id (FK), note (text, nullable — recipe-specific context, e.g.
  why this technique/reaction matters *in this recipe*), step_id (FK to Step,
  nullable), ingredient_id (FK to Ingredient, nullable), position. Generated
  at ingestion time: Claude tags the relevant glossary term(s) per
  step/ingredient and writes the short recipe-specific note. Nullable
  step/ingredient FKs let a callout be anchored inline where relevant, or
  left general when it isn't about one specific line.
- **SavedRecipe** (cookbook entry) — id, user_id (FK), recipe_id (FK),
  saved_at, unique(user_id, recipe_id)

Ingredients, steps, and insights are child rows (not JSON blobs) so scaling,
the scannable-structure view, and inline insight anchoring can all operate on
typed data. Substitutions and adaptations are still **not persisted** for
MVP — computed on demand via Claude each time; the glossary is the one
exception to "don't persist LLM output," because its content is fixed
reference knowledge rather than a per-recipe generation, so it's seeded once
(e.g. a migration/fixture) rather than regenerated on every ingestion.

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
