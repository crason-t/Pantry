import { Link } from "react-router-dom";
import type { RecipeCardSummary } from "../api/types";

export function RecipeCard({ recipe }: { recipe: RecipeCardSummary }) {
  const hasMeta = recipe.servings != null || recipe.total_time != null;

  return (
    <Link to={`/recipes/${recipe.id}`} className="recipe-card">
      <h3 className="recipe-card-title">{recipe.title}</h3>
      {hasMeta && (
        <p className="recipe-card-meta">
          {recipe.servings != null && <span>Serves {recipe.servings}</span>}
          {recipe.servings != null && recipe.total_time != null && <span aria-hidden="true"> · </span>}
          {recipe.total_time != null && <span>{recipe.total_time}</span>}
        </p>
      )}
    </Link>
  );
}
