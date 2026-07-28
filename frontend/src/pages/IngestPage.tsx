import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { ApiError, apiPostJson } from "../api/client";
import type { Recipe } from "../api/types";

export function IngestPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState<"url" | "text">("url");
  const [url, setUrl] = useState("");
  const [text, setText] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);
    try {
      const payload = mode === "url" ? { url } : { text };
      const recipe = await apiPostJson<Recipe>("/recipes/ingest", payload);
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
      <div role="radiogroup" aria-label="Ingest source">
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
        ) : (
          <label>
            Recipe text
            <textarea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={12}
              required
            />
          </label>
        )}
        {error && <p role="alert">{error}</p>}
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "Ingesting..." : "Ingest recipe"}
        </button>
      </form>
    </div>
  );
}
