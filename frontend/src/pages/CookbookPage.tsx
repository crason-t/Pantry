import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiGet } from "../api/client";
import type { RecipeSummary } from "../api/types";
import { RecipeCard } from "../components/RecipeCard";

export function CookbookPage() {
  const [recipes, setRecipes] = useState<RecipeSummary[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    apiGet<RecipeSummary[]>("/recipes/cookbook")
      .then(setRecipes)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
  }, []);

  return (
    <div>
      <h1>Cookbook</h1>

      {error && <p role="alert">{error}</p>}
      {recipes === null && !error && <p>Loading...</p>}
      {recipes !== null && recipes.length === 0 && (
        <div className="cookbook-empty">
          <p>No saved recipes yet.</p>
          <p className="cookbook-empty-hint">Ingest a recipe from a URL or pasted text to start your cookbook.</p>
          <Link to="/recipes/new" className="btn-primary">
            Add a recipe
          </Link>
        </div>
      )}
      {recipes !== null && recipes.length > 0 && (
        <div className="recipe-card-grid">
          {recipes.map((recipe) => (
            <RecipeCard key={recipe.id} recipe={recipe} />
          ))}
        </div>
      )}
    </div>
  );
}
