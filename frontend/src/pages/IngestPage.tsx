import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, apiPostJson } from "../api/client";
import type { Recipe } from "../api/types";

export function IngestPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"url" | "text" | "recommend">("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const recipe =
        mode === "recommend"
          ? await apiPostJson<Recipe>("/recipes/recommend", {})
          : await apiPostJson<Recipe>(
              "/recipes/ingest",
              mode === "url" ? { url } : { text },
            );
      navigate(`/recipes/${recipe.id}`);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <div>
      <h1>Ingest a recipe</h1>
      <div className="mode-toggle" role="radiogroup" aria-label="Ingest source">
        <label>
          <input
            type="radio"
            checked={mode === "url"}
            onChange={() => setMode("url")}
          />
          From a URL
        </label>
        <label>
          <input
            type="radio"
            checked={mode === "text"}
            onChange={() => setMode("text")}
          />
          Paste recipe text
        </label>
        <label>
          <input
            type="radio"
            checked={mode === "recommend"}
            onChange={() => setMode("recommend")}
          />
          Recommend from my cookbook
        </label>
      </div>
      <form onSubmit={handleSubmit}>
        {mode === "url" ? (
          <label>
            Recipe URL
            <input
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com/some-recipe"
              required
            />
          </label>
        ) : mode === "text" ? (
          <label>
            Recipe text
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              required
            />
          </label>
        ) : (
          <p>
            Pantry will look at the recipes saved in your cookbook and suggest
            a new recipe to match those tastes. No input needed — just hit the
            button.
          </p>
        )}
        {error && <p role="alert">{error}</p>}
        <button type="submit" className="btn-primary" disabled={isSubmitting}>
          {mode === "recommend"
            ? isSubmitting
              ? "Finding a recipe..."
              : "Recommend a recipe"
            : isSubmitting
              ? "Ingesting..."
              : "Ingest recipe"}
        </button>
      </form>
    </div>
  );
}
