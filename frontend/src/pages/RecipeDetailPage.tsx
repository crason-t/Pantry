import { useParams } from "react-router-dom";

export function RecipeDetailPage() {
  const { id } = useParams();
  return (
    <div>
      <h1>Recipe {id}</h1>
      <p>
        Placeholder -- structured view, "why this works" insights,
        substitutions, adaptation, and scaling land in later steps.
      </p>
    </div>
  );
}
