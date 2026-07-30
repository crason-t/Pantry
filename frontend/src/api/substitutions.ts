import { apiPost } from "./client";
import type { SubstitutionSuggestions } from "./types";

// On-demand only -- nothing here is saved, so there's no GET counterpart.
// Re-fetched fresh every time the user asks (see docs/MVP.md data model
// summary: substitutions are computed on demand via Claude, not persisted).
export function fetchIngredientSubstitutions(
  recipeId: number | string,
  ingredientId: number,
): Promise<SubstitutionSuggestions> {
  return apiPost<SubstitutionSuggestions>(
    `/recipes/${recipeId}/ingredients/${ingredientId}/substitutions`,
  );
}
