import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ApiError, apiGet } from "../api/client";
import type { RecipeSummary } from "../api/types";
import { useAuth } from "../context/AuthContext";

export function CookbookPage() {
  const { user, logout } = useAuth();
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
      <p>Logged in as {user?.email}</p>
      <button type="button" onClick={logout}>
        Log out
      </button>
      <p>
        <Link to="/recipes/new">Ingest a recipe</Link>
      </p>

      {error && <p role="alert">{error}</p>}
      {recipes === null && !error && <p>Loading...</p>}
      {recipes !== null && recipes.length === 0 && <p>No saved recipes yet.</p>}
      {recipes !== null && recipes.length > 0 && (
        <ul>
          {recipes.map((recipe) => (
            <li key={recipe.id}>
              <Link to={`/recipes/${recipe.id}`}>{recipe.title}</Link>
              {recipe.servings != null && ` — serves ${recipe.servings}`}
              {recipe.total_time && ` — ${recipe.total_time}`}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
