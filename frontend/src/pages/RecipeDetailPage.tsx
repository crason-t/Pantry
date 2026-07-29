import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { ApiError, apiGet, apiPost } from "../api/client";
import { getCustomizedIngredients, saveCustomizedIngredients } from "../api/ingredientCustomizations";
import { fetchIngredientSubstitutions } from "../api/substitutions";
import type { CustomizedIngredients, Ingredient, IngredientListEdit, MergedIngredient, Recipe, SubstitutionSuggestion } from "../api/types";
import { InsightCallout } from "../components/InsightCallout";
import { InsightCard } from "../components/InsightCard";
import { InsightTag } from "../components/InsightTag";
import { StepCard } from "../components/StepCard";
import { SubstitutionPanel, type SubstitutionPanelState } from "../components/SubstitutionPanel";
import { CATEGORY_LABEL } from "../components/insightCategory";

type StepView = "list" | "cards";

// A row in the ingredient editor's local draft state -- mirrors
// IngredientEdit, but as plain editable strings for controlled inputs.
interface EditableIngredientRow {
  ingredient_id: number | null;
  quantity: string;
  unit: string;
  name: string;
}

export function RecipeDetailPage() {
  const { id } = useParams();
  const [recipe, setRecipe] = useState<Recipe | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saveState, setSaveState] = useState<"idle" | "saving" | "saved">("idle");
  const [stepView, setStepView] = useState<StepView>("list");

  // This user's customized ingredient list (canonical ingredients merged
  // with their own add/edit overlay -- see api/ingredientCustomizations.ts).
  // Null until the first fetch resolves; falls back to the recipe's plain
  // canonical ingredients below until then.
  const [customized, setCustomized] = useState<CustomizedIngredients | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editRows, setEditRows] = useState<EditableIngredientRow[]>([]);
  const [savingEdits, setSavingEdits] = useState(false);
  const [editError, setEditError] = useState<string | null>(null);
  const [editNotice, setEditNotice] = useState<string | null>(null);

  useEffect(() => {
    apiGet<Recipe>(`/recipes/${id}`)
      .then(setRecipe)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Something went wrong"));
  }, [id]);

  useEffect(() => {
    if (!id) return;
    getCustomizedIngredients(id)
      .then(setCustomized)
      .catch(() => setCustomized(null)); // fall back to canonical ingredients below
  }, [id]);

  const { insightsByIngredientId, insightsByStepId, generalInsights } = useMemo(() => {
    const byIngredient = new Map<number, Recipe["insights"]>();
    const byStep = new Map<number, Recipe["insights"]>();
    const general: Recipe["insights"] = [];

    for (const insight of recipe?.insights ?? []) {
      if (insight.ingredient_id != null) {
        const list = byIngredient.get(insight.ingredient_id) ?? [];
        list.push(insight);
        byIngredient.set(insight.ingredient_id, list);
      } else if (insight.step_id != null) {
        const list = byStep.get(insight.step_id) ?? [];
        list.push(insight);
        byStep.set(insight.step_id, list);
      } else {
        general.push(insight);
      }
    }
    return { insightsByIngredientId: byIngredient, insightsByStepId: byStep, generalInsights: general };
  }, [recipe]);

  // Prefer the merged (canonical + this user's overlay) ingredient list once
  // it has loaded; fall back to the recipe's plain canonical ingredients
  // beforehand (or if the user hasn't saved this recipe, in which case the
  // merge is a no-op anyway -- see get_customized_ingredients on the backend).
  const displayIngredients: MergedIngredient[] = useMemo(() => {
    if (customized) {
      return customized.ingredients;
    }
    return (recipe?.ingredients ?? []).map((ingredient) => ({
      ingredient_id: ingredient.id,
      customization_id: null,
      position: ingredient.position,
      quantity: ingredient.quantity,
      unit: ingredient.unit,
      colloquial_quantity: ingredient.colloquial_quantity,
      name: ingredient.name,
      component: ingredient.component,
      notes: ingredient.notes,
      raw_text: ingredient.raw_text,
      is_custom: false,
    }));
  }, [customized, recipe]);

  const ingredientGroups = useMemo(() => {
    const order: (string | null)[] = [];
    const seen = new Set<string | null>();
    for (const ingredient of displayIngredients) {
      if (!seen.has(ingredient.component)) {
        seen.add(ingredient.component);
        order.push(ingredient.component);
      }
    }
    return order.map((component) => ({
      component,
      items: displayIngredients.filter((ingredient) => ingredient.component === component),
    }));
  }, [displayIngredients]);
  const showGroupHeaders = ingredientGroups.length > 1 || ingredientGroups[0]?.component != null;

  const stepTipsSummary = useMemo(() => {
    const steps = recipe?.steps ?? [];
    return steps.flatMap((step, index) =>
      (insightsByStepId.get(step.id) ?? []).map((insight) => ({ stepNumber: index + 1, insight })),
    );
  }, [recipe, insightsByStepId]);

  async function handleSave() {
    setSaveState("saving");
    try {
      await apiPost(`/recipes/${id}/save`);
      setSaveState("saved");
      // Saving flips is_saved server-side, which is what unlocks ingredient
      // customization -- refetch so the "Edit ingredients" affordance
      // updates without a full page reload.
      if (id) {
        getCustomizedIngredients(id)
          .then(setCustomized)
          .catch(() => undefined);
      }
    } catch {
      setSaveState("idle");
    }
  }

  function handleStartEditing() {
    if (!customized?.is_saved) {
      setEditNotice("Save this recipe to your cookbook before customizing its ingredients.");
      return;
    }
    setEditNotice(null);
    setEditError(null);
    setEditRows(
      displayIngredients.map((ingredient) => ({
        ingredient_id: ingredient.ingredient_id,
        quantity: ingredient.quantity ?? "",
        unit: ingredient.unit ?? "",
        name: ingredient.name,
      })),
    );
    setIsEditing(true);
  }

  function handleCancelEditing() {
    setIsEditing(false);
    setEditError(null);
  }

  function updateEditRow(index: number, changes: Partial<EditableIngredientRow>) {
    setEditRows((rows) => rows.map((row, i) => (i === index ? { ...row, ...changes } : row)));
  }

  function handleAddIngredientRow() {
    setEditRows((rows) => [...rows, { ingredient_id: null, quantity: "", unit: "", name: "" }]);
  }

  async function handleSaveEdits() {
    if (!id) return;
    const payload: IngredientListEdit = {
      items: editRows
        .filter((row) => row.name.trim() !== "")
        .map((row) => ({
          ingredient_id: row.ingredient_id,
          quantity: row.quantity.trim() || null,
          unit: row.unit.trim() || null,
          name: row.name.trim(),
        })),
      removed_ingredient_ids: [],
    };
    setSavingEdits(true);
    setEditError(null);
    try {
      const result = await saveCustomizedIngredients(id, payload);
      setCustomized(result);
      setIsEditing(false);
    } catch (err) {
      setEditError(err instanceof ApiError ? err.message : "Something went wrong saving your changes");
    } finally {
      setSavingEdits(false);
    }
  }

  if (error) {
    return <p role="alert">{error}</p>;
  }
  if (!recipe) {
    return <p>Loading...</p>;
  }

  return (
    <div>
      <h1>{recipe.title}</h1>
      <p>
        {recipe.servings != null && <>Serves {recipe.servings}. </>}
        {recipe.prep_time && <>Prep: {recipe.prep_time}. </>}
        {recipe.cook_time && <>Cook: {recipe.cook_time}. </>}
        {recipe.total_time && <>Total: {recipe.total_time}. </>}
      </p>
      {recipe.equipment.length > 0 && (
        <p>Equipment: {recipe.equipment.join(", ")}</p>
      )}

      <button type="button" className="btn-primary" onClick={handleSave} disabled={saveState !== "idle"}>
        {saveState === "saved" ? "Saved to cookbook" : saveState === "saving" ? "Saving..." : "Save to cookbook"}
      </button>
      <p>
        <Link to={`/recipes/${recipe.id}/cook`} className="btn-secondary">
          Start cooking
        </Link>
      </p>

      {recipe.tips.length > 0 && (
        <section aria-label="Tips">
          <h2>Tips</h2>
          <ul className="tips-list">
            {recipe.tips.map((tip) => (
              <li className="tip-row" key={tip.id}>
                <span className="tip-marker" aria-hidden="true">!</span>
                <span className="tip-text">{tip.tip_text}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {generalInsights.length > 0 && (
        <section aria-label="Why this dish works">
          <h2>Why this dish works</h2>
          <div className="insight-card-grid">
            {generalInsights.map((insight) => (
              <InsightCard key={insight.id} insight={insight} />
            ))}
          </div>
        </section>
      )}

      <div className="ingredients-header">
        <h2>Ingredients</h2>
        {!isEditing && (
          <button type="button" className="btn-secondary" onClick={handleStartEditing}>
            Edit ingredients
          </button>
        )}
      </div>
      {editNotice && !isEditing && <p className="ingredient-edit-notice">{editNotice}</p>}

      {isEditing ? (
        <div className="ingredient-edit-list">
          {editRows.map((row, index) => (
            <div className="ingredient-edit-row" key={index}>
              <input
                type="text"
                className="ingredient-edit-qty"
                placeholder="Qty"
                value={row.quantity}
                onChange={(e) => updateEditRow(index, { quantity: e.target.value })}
                aria-label="Quantity"
              />
              <input
                type="text"
                className="ingredient-edit-unit"
                placeholder="Unit"
                value={row.unit}
                onChange={(e) => updateEditRow(index, { unit: e.target.value })}
                aria-label="Unit"
              />
              <input
                type="text"
                className="ingredient-edit-name"
                placeholder="Ingredient name"
                value={row.name}
                onChange={(e) => updateEditRow(index, { name: e.target.value })}
                aria-label="Ingredient name"
              />
            </div>
          ))}
          <button type="button" className="btn-ghost" onClick={handleAddIngredientRow}>
            + Add ingredient
          </button>
          {editError && <p role="alert">{editError}</p>}
          <div className="ingredient-edit-actions">
            <button type="button" className="btn-primary" onClick={handleSaveEdits} disabled={savingEdits}>
              {savingEdits ? "Saving..." : "Save"}
            </button>
            <button type="button" className="btn-ghost" onClick={handleCancelEditing} disabled={savingEdits}>
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="ingredient-list">
          {ingredientGroups.map((group) => (
            <div className="ingredient-group" key={group.component ?? "__ungrouped"}>
              {showGroupHeaders && group.component && (
                <h3 className="ingredient-group-title">{group.component}</h3>
              )}
              {group.items.map((ingredient) => (
                <IngredientRow
                  key={`${ingredient.ingredient_id ?? "new"}-${ingredient.customization_id ?? "canonical"}`}
                  recipeId={recipe.id}
                  ingredient={{
                    id: ingredient.ingredient_id ?? 0,
                    position: ingredient.position,
                    quantity: ingredient.quantity,
                    unit: ingredient.unit,
                    colloquial_quantity: ingredient.colloquial_quantity,
                    name: ingredient.name,
                    notes: ingredient.notes,
                    raw_text: ingredient.raw_text,
                    component: ingredient.component,
                  }}
                  insights={
                    ingredient.ingredient_id != null
                      ? (insightsByIngredientId.get(ingredient.ingredient_id) ?? [])
                      : []
                  }
                />
              ))}
            </div>
          ))}
        </div>
      )}

      {stepTipsSummary.length > 0 && (
        <div className="step-tips-summary">
          <h3>Keys of the recipe</h3>
          <ul className="step-tips-list">
            {stepTipsSummary.map(({ stepNumber, insight }) => (
              <li className="step-tip-row" key={insight.id}>
                <span className="step-tip-number">{stepNumber}</span>
                <div className="step-tip-body">
                  <span className="insight-badge">
                    {CATEGORY_LABEL[insight.glossary_term.category] ?? insight.glossary_term.category}
                    {" · "}
                    {insight.glossary_term.name}
                  </span>
                  {insight.note && <p className="insight-note">{insight.note}</p>}
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div className="steps-header">
        <h2>Steps</h2>
        <div className="view-toggle" role="tablist" aria-label="Steps view">
          <button
            type="button"
            role="tab"
            aria-selected={stepView === "list"}
            className={stepView === "list" ? "active" : ""}
            onClick={() => setStepView("list")}
          >
            List
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={stepView === "cards"}
            className={stepView === "cards" ? "active" : ""}
            onClick={() => setStepView("cards")}
          >
            Cards
          </button>
        </div>
      </div>

      {stepView === "list" ? (
        <ol className="step-list">
          {recipe.steps.map((step, index) => (
            <li className="step-row" key={step.id}>
              <span className="step-number">{index + 1}</span>
              <div className="step-body">
                <p className="step-instruction">{step.instruction}</p>
                {(insightsByStepId.get(step.id) ?? []).map((insight) => (
                  <InsightCallout key={insight.id} insight={insight} />
                ))}
              </div>
            </li>
          ))}
        </ol>
      ) : (
        <div className="step-card-grid">
          {recipe.steps.map((step, index) => (
            <StepCard
              key={step.id}
              index={index}
              instruction={step.instruction}
              insights={insightsByStepId.get(step.id) ?? []}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function IngredientRow({
  recipeId,
  ingredient,
  insights,
}: {
  recipeId: number;
  ingredient: Ingredient;
  insights: Recipe["insights"];
}) {
  const [subState, setSubState] = useState<SubstitutionPanelState | "closed">("closed");
  const [suggestions, setSuggestions] = useState<SubstitutionSuggestion[]>([]);
  const [subError, setSubError] = useState<string | null>(null);

  async function handleToggleSubstitutions() {
    if (subState === "open" || subState === "loading") {
      setSubState("closed");
      return;
    }
    setSubState("loading");
    setSubError(null);
    try {
      const result = await fetchIngredientSubstitutions(recipeId, ingredient.id);
      setSuggestions(result.suggestions);
      setSubState("open");
    } catch (err) {
      setSubError(err instanceof ApiError ? err.message : "Could not load substitutions");
      setSubState("error");
    }
  }

  const precise = [ingredient.quantity, ingredient.unit].filter(Boolean).join(" ");
  const primary = ingredient.colloquial_quantity || precise;
  const secondary = ingredient.colloquial_quantity ? precise : null;
  return (
    <div className="ingredient-row-wrap">
      <div className="ingredient-row">
        <span className="ingredient-name">
          <button
            type="button"
            className="ingredient-name-btn"
            onClick={handleToggleSubstitutions}
            aria-expanded={subState === "open"}
            aria-label={`Substitute suggestions for ${ingredient.name}`}
          >
            {ingredient.raw_text}
          </button>
          {insights.map((insight) => (
            <InsightTag key={insight.id} insight={insight} />
          ))}
        </span>
        {primary && (
          <span className="ingredient-qty-group">
            <span className="ingredient-qty">{primary}</span>
            {secondary && <span className="ingredient-qty-secondary">{secondary}</span>}
          </span>
        )}
      </div>
      {subState !== "closed" && (
        <SubstitutionPanel
          state={subState}
          suggestions={suggestions}
          error={subError}
          onDismiss={() => setSubState("closed")}
        />
      )}
    </div>
  );
}
