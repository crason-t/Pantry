import type { RecipeInsight } from "../api/types";

const CATEGORY_LABEL: Record<string, string> = {
  flavor: "Flavor",
  technique: "Technique",
  reaction: "Reaction",
};

export function InsightCallout({ insight }: { insight: RecipeInsight }) {
  return (
    <div className="insight-callout" data-category={insight.glossary_term.category}>
      <span className="insight-badge">
        {CATEGORY_LABEL[insight.glossary_term.category] ?? insight.glossary_term.category}
        {" · "}
        {insight.glossary_term.name}
      </span>
      {insight.note && <p className="insight-note">{insight.note}</p>}
    </div>
  );
}
