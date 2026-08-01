import { useEffect, useState } from "react";
import { ApiError, apiGet, apiPostJson } from "../api/client";
import type { RecommendedRecipe } from "../api/types";
import { RecipeCard } from "../components/RecipeCard";

export function HomePage() {
  const [recommendations, setRecommendations] = useState<RecommendedRecipe[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    apiGet<RecommendedRecipe[]>("/recipes/recommendations")
      .then(setRecommendations)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
  }, []);

  async function handleGenerate() {
    setError(null);
    setIsGenerating(true);
    try {
      const batch = await apiPostJson<RecommendedRecipe[]>("/recipes/recommendations", {});
      setRecommendations(batch);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setIsGenerating(false);
    }
  }

  const generateButton = (label: string) => (
    <button
      type="button"
      className="btn-primary"
      onClick={handleGenerate}
      disabled={isGenerating}
    >
      {isGenerating ? "Finding recipes..." : label}
    </button>
  );

  return (
    <div>
      <h1>Home</h1>

      <section>
        <h2>Recommended Recipes</h2>
        {error && <p role="alert">{error}</p>}
        {recommendations === null && !error && <p>Loading...</p>}
        {recommendations !== null && recommendations.length === 0 && (
          <div className="cookbook-empty">
            <p>No recommendations yet.</p>
            <p className="cookbook-empty-hint">
              Pantry can look at the recipes saved in your cookbook and suggest
              new recipes to match those tastes.
            </p>
            {generateButton("Recommend recipes")}
          </div>
        )}
        {recommendations !== null && recommendations.length > 0 && (
          <>
            <div className="recipe-card-grid">
              {recommendations.map((recipe) => (
                <RecipeCard key={recipe.id} recipe={recipe} />
              ))}
            </div>
            {generateButton("Refresh recommendations")}
          </>
        )}
        {isGenerating && (
          <p>
            This can take a minute or two — Pantry is generating three new
            recipes and their insights.
          </p>
        )}
      </section>
    </div>
  );
}
