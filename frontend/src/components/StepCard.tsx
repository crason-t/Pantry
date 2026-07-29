import { useState } from "react";
import type { Recipe } from "../api/types";
import { CATEGORY_LABEL } from "./insightCategory";

export function StepCard({
  index,
  instruction,
  insights,
}: {
  index: number;
  instruction: string;
  insights: Recipe["insights"];
}) {
  const [flipped, setFlipped] = useState(false);

  function toggle() {
    setFlipped((f) => !f);
  }

  return (
    <div
      className={`step-card${flipped ? " flipped" : ""}`}
      role="button"
      tabIndex={0}
      aria-pressed={flipped}
      onClick={toggle}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          toggle();
        }
      }}
    >
      <div className="step-card-inner">
        <div className="step-card-face step-card-front">
          <span className="step-number">{index + 1}</span>
          <p className="step-instruction">{instruction}</p>
          <span className="step-card-hint">
            {insights.length > 0 ? "Tap for tips" : "Tap to flip"}
          </span>
        </div>
        <div className="step-card-face step-card-back">
          <span className="step-card-hint">Step {index + 1}</span>
          {insights.length > 0 ? (
            insights.map((insight) => (
              <div className="step-card-tip" key={insight.id} data-category={insight.glossary_term.category}>
                <span className="insight-badge">
                  {CATEGORY_LABEL[insight.glossary_term.category] ?? insight.glossary_term.category}
                  {" · "}
                  {insight.glossary_term.name}
                </span>
                {insight.note && <p className="insight-note">{insight.note}</p>}
              </div>
            ))
          ) : (
            <p className="insight-note">No extra tips for this step.</p>
          )}
        </div>
      </div>
    </div>
  );
}
