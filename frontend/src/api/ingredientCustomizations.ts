import { apiGet, apiPutJson } from "./client";
import type { CustomizedIngredients, IngredientListEdit } from "./types";

export function getCustomizedIngredients(recipeId: number | string): Promise<CustomizedIngredients> {
  return apiGet<CustomizedIngredients>(`/recipes/${recipeId}/ingredients/customized`);
}

export function saveCustomizedIngredients(
  recipeId: number | string,
  payload: IngredientListEdit,
): Promise<CustomizedIngredients> {
  return apiPutJson<CustomizedIngredients>(`/recipes/${recipeId}/ingredients/customized`, payload);
}
