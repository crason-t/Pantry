import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiGet, apiPost } from "../api/client";
import type { Recipe } from "../api/types";
import { InsightCallout } from "../components/InsightCallout";

export function RecipeDetailPage() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved">("idle");

  useEffect(() => {
    apiGet<Recipe>(`/recipes/${id}`)
      .then(setRecipe)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
  }, [id]);

  const { insightsByIngredientId, insightsByStepId, generalInsights } = useMemo(() => {
    const byIngredient = new Map<number, Recipe["insights"]>();
    const byStep = new Map<number, Recipe["insights"]>();
    const general: Recipe["insights"] = [];

    for (const insight of recipe?.insights ?? []) {
      if (insight.ingredient_id != null) {
        const list = byIngredient.get(insight.ingredient_id) ?? [];
        list.push(insight);
        byIngredient.set(insight.ingredient_id, list);
      } else if (insight.step_id != null) {
        const list = byStep.get(insight.step_id) ?? [];
        list.push(insight);
        byStep.set(insight.step_id, list);
      } else {
        general.push(insight);
      }
    }
    return { insightsByIngredientId: byIngredient, insightsByStepId: byStep, generalInsights: general };
  }, [recipe]);

  async function handleSave() {
    setSaveState("saving");
    try {
      await apiPost(`/recipes/${id}/save`);
      setSaveState("saved");
    } catch {
      setSaveState("idle");
    }
  }

  if (error) {
    return <p role="alert">{error}</p>;
  }
  if (!recipe) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>{recipe.title}</h1>
      <p>
        {recipe.servings != null && <>Serves {recipe.servings}. </>}
        {recipe.prep_time && <>Prep: {recipe.prep_time}. </>}
        {recipe.cook_time && <>Cook: {recipe.cook_time}. </>}
        {recipe.total_time && <>Total: {recipe.total_time}. </>}
      </p>
      {recipe.equipment.length > 0 && (
        <p>Equipment: {recipe.equipment.join(", ")}</p>
      )}

      <button type="button" onClick={handleSave} disabled={saveState !== "idle"}>
        {saveState === "saved" ? "Saved to cookbook" : saveState === "saving" ? "Saving..." : "Save to cookbook"}
      </button>
      <p>
        <Link to={`/recipes/${recipe.id}/cook`}>Start cooking</Link>
      </p>

      {generalInsights.length > 0 && (
        <section aria-label="Why this dish works">
          <h2>Why this dish works</h2>
          {generalInsights.map((insight) => (
            <InsightCallout key={insight.id} insight={insight} />
          ))}
        </section>
      )}

      <h2>Ingredients</h2>
      <ul>
        {recipe.ingredients.map((ingredient) => (
          <li key={ingredient.id}>
            {ingredient.raw_text}
            {(insightsByIngredientId.get(ingredient.id) ?? []).map((insight) => (
              <InsightCallout key={insight.id} insight={insight} />
            ))}
          </li>
        ))}
      </ul>

      <h2>Steps</h2>
      <ol>
        {recipe.steps.map((step) => (
          <li key={step.id}>
            {step.instruction}
            {(insightsByStepId.get(step.id) ?? []).map((insight) => (
              <InsightCallout key={insight.id} insight={insight} />
            ))}
          </li>
        ))}
      </ol>
    </div>
  );
}
