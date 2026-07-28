import { useParams } from "react-router-dom";

export function CookModePage() {
  const { id } = useParams();
  return (
    <div>
      <h1>Cook mode: Recipe {id}</h1>
      <p>Placeholder -- guided step-by-step tap next/back UI lands later.</p>
    </div>
  );
}
