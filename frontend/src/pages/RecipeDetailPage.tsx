import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiGet, apiPost } from "../api/client";
import type { Ingredient, Recipe } from "../api/types";
import { InsightCallout } from "../components/InsightCallout";
import { InsightTag } from "../components/InsightTag";

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

  const ingredientGroups = useMemo(() => {
    const ingredients = recipe?.ingredients ?? [];
    const order: (string | null)[] = [];
    const seen = new Set<string | null>();
    for (const ingredient of ingredients) {
      if (!seen.has(ingredient.component)) {
        seen.add(ingredient.component);
        order.push(ingredient.component);
      }
    }
    return order.map((component) => ({
      component,
      items: ingredients.filter((ingredient) => ingredient.component === component),
    }));
  }, [recipe]);
  const showGroupHeaders = ingredientGroups.length > 1 || ingredientGroups[0]?.component != null;

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
      <div className="ingredient-list">
        {ingredientGroups.map((group) => (
          <div className="ingredient-group" key={group.component ?? "__ungrouped"}>
            {showGroupHeaders && group.component && (
              <h3 className="ingredient-group-title">{group.component}</h3>
            )}
            {group.items.map((ingredient) => (
              <IngredientRow
                key={ingredient.id}
                ingredient={ingredient}
                insights={insightsByIngredientId.get(ingredient.id) ?? []}
              />
            ))}
          </div>
        ))}
      </div>

      <h2>Steps</h2>
      <ol className="step-list">
        {recipe.steps.map((step, index) => (
          <li className="step-row" key={step.id}>
            <span className="step-number">{index + 1}</span>
            <div className="step-body">
              <p className="step-instruction">{step.instruction}</p>
              {(insightsByStepId.get(step.id) ?? []).map((insight) => (
                <InsightCallout key={insight.id} insight={insight} />
              ))}
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}

function IngredientRow({
  ingredient,
  insights,
}: {
  ingredient: Ingredient;
  insights: Recipe["insights"];
}) {
  const precise = [ingredient.quantity, ingredient.unit].filter(Boolean).join(" ");
  const primary = ingredient.colloquial_quantity || precise;
  const secondary = ingredient.colloquial_quantity ? precise : null;
  return (
    <div className="ingredient-row">
      <span className="ingredient-name">
        {ingredient.raw_text}
        {insights.map((insight) => (
          <InsightTag key={insight.id} insight={insight} />
        ))}
      </span>
      {primary && (
        <span className="ingredient-qty-group">
          <span className="ingredient-qty">{primary}</span>
          {secondary && <span className="ingredient-qty-secondary">{secondary}</span>}
        </span>
      )}
    </div>
  );
}
