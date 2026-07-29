import type { RecipeInsight } from "../api/types";

export function InsightTag({ insight }: { insight: RecipeInsight }) {
  return (
    <span
      className="insight-tag"
      data-category={insight.glossary_term.category}
      title={insight.note ?? insight.glossary_term.definition}
    >
      {insight.glossary_term.name}
    </span>
  );
}
