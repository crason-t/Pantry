import type { SubstitutionSuggestion } from "../api/types";

export type SubstitutionPanelState = "loading" | "open" | "error";

// Inline, dismissible, expands in place under the ingredient row it belongs
// to -- nothing here is saved, it's re-fetched fresh each time (see
// docs/MVP.md: substitutions are computed on demand, never persisted).
export function SubstitutionPanel({
  state,
  suggestions,
  error,
  onDismiss,
}: {
  state: SubstitutionPanelState;
  suggestions: SubstitutionSuggestion[];
  error: string | null;
  onDismiss: () => void;
}) {
  return (
    <div className="substitution-panel" role="region" aria-label="Substitution suggestions">
      <div className="substitution-panel-header">
        <span className="substitution-panel-title">Substitutes</span>
        <button type="button" className="btn-ghost substitution-panel-dismiss" onClick={onDismiss}>
          Dismiss
        </button>
      </div>

      {state === "loading" && <p className="substitution-panel-status">Asking Claude for substitutes...</p>}

      {state === "error" && (
        <p className="substitution-panel-status" role="alert">
          {error}
        </p>
      )}

      {state === "open" && suggestions.length === 0 && (
        <p className="substitution-panel-status">No good substitutes turned up for this one.</p>
      )}

      {state === "open" && suggestions.length > 0 && (
        <ul className="substitution-list">
          {suggestions.map((suggestion, index) => (
            <li className="substitution-item" key={index}>
              <span className="substitution-name">{suggestion.substitute}</span>
              <span className="substitution-reason">{suggestion.reason}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
