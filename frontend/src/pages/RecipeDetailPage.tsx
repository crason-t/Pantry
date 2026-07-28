import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiGet, apiPost } from "../api/client";
import type { Recipe } from "../api/types";

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

      <h2>Ingredients</h2>
      <ul>
        {recipe.ingredients.map((ingredient) => (
          <li key={ingredient.id}>{ingredient.raw_text}</li>
        ))}
      </ul>

      <h2>Steps</h2>
      <ol>
        {recipe.steps.map((step) => (
          <li key={step.id}>{step.instruction}</li>
        ))}
      </ol>
    </div>
  );
}
