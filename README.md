# Pantry

A recipe assistant: ingest a recipe (URL or pasted text), get it reformatted into
a scannable structure, understand the culinary "why" behind it, get ingredient
substitutions and equipment/method adaptations, scale servings, and get guided
step-by-step through cooking it. Save recipes to a personal cookbook.

Long-term vision is a full home pantry/inventory + recipe + grocery-budget
assistant; this repo currently scopes only the recipe-assistant MVP.

See `docs/MVP.md` for the full feature spec and architecture decisions.

## Status

Backend and frontend are built and working end-to-end (auth, recipe
ingestion, "why this dish works" insights, cookbook save/list); several
features remain (substitutions, adaptations, serving-scale, guided cook
mode). See `docs/PROJECT_PLAN.md` for the build-sequence checklist and
`SESSION_LOG.md` for session-by-session detail.
