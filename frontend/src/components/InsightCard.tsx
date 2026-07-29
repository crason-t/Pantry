import type { RecipeInsight } from "../api/types";
import { CATEGORY_LABEL } from "./insightCategory";

export function InsightCard({ insight }: { insight: RecipeInsight }) {
  return (
    <div className="insight-card" data-category={insight.glossary_term.category}>
      <span className="insight-badge">
        {CATEGORY_LABEL[insight.glossary_term.category] ?? insight.glossary_term.category}
        {" · "}
        {insight.glossary_term.name}
      </span>
      {insight.note && <p className="insight-note">{insight.note}</p>}
    </div>
  );
}
