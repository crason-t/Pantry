from sqlalchemy.orm import Session

from app.models.ingredient_customization import CustomizationAction, IngredientCustomization
from app.models.recipe import Recipe
from app.models.saved_recipe import SavedRecipe
from app.schemas.ingredient_customization import IngredientListEdit, MergedIngredientRead


def _raw_text(quantity: str | None, unit: str | None, name: str) -> str:
    """Rebuild a display raw_text for an overridden row, in the same
    "<qty> <unit> <name>" shape the ingestion pipeline produces."""
    prefix = " ".join(part for part in (quantity, unit) if part)
    return f"{prefix} {name}".strip() if prefix else name


def merge_ingredients(
    recipe: Recipe, customizations: list[IngredientCustomization]
) -> list[MergedIngredientRead]:
    """Overlay a user's IngredientCustomization rows onto a recipe's
    canonical Ingredient rows. Never mutates either -- always builds a new
    read-only view. Canonical ingredients keep their catalog order; a
    user's own added lines are appended after them, ordered by position.

    See models/ingredient_customization.py for why this can't just edit
    Ingredient rows in place.
    """
    overrides_by_ingredient_id = {
        c.ingredient_id: c for c in customizations if c.action != CustomizationAction.ADD
    }

    merged: list[MergedIngredientRead] = []
    for ingredient in recipe.ingredients:
        override = overrides_by_ingredient_id.get(ingredient.id)
        if override is not None and override.action == CustomizationAction.REMOVE:
            continue
        if override is not None and override.action == CustomizationAction.MODIFY:
            name = override.name or ingredient.name
            merged.append(
                MergedIngredientRead(
                    ingredient_id=ingredient.id,
                    customization_id=override.id,
                    position=ingredient.position,
                    quantity=override.quantity,
                    unit=override.unit,
                    colloquial_quantity=ingredient.colloquial_quantity,
                    name=name,
                    component=ingredient.component,
                    notes=ingredient.notes,
                    raw_text=_raw_text(override.quantity, override.unit, name),
                    is_custom=False,
                )
            )
            continue
        merged.append(
            MergedIngredientRead(
                ingredient_id=ingredient.id,
                customization_id=None,
                position=ingredient.position,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                colloquial_quantity=ingredient.colloquial_quantity,
                name=ingredient.name,
                component=ingredient.component,
                notes=ingredient.notes,
                raw_text=ingredient.raw_text,
                is_custom=False,
            )
        )

    added = sorted(
        (c for c in customizations if c.action == CustomizationAction.ADD),
        key=lambda c: c.position,
    )
    for override in added:
        name = override.name or ""
        merged.append(
            MergedIngredientRead(
                ingredient_id=None,
                customization_id=override.id,
                position=override.position,
                quantity=override.quantity,
                unit=override.unit,
                colloquial_quantity=None,
                name=name,
                component=None,
                notes=None,
                raw_text=_raw_text(override.quantity, override.unit, name),
                is_custom=True,
            )
        )
    return merged


def save_ingredient_customizations(
    db: Session, saved_recipe: SavedRecipe, recipe: Recipe, payload: IngredientListEdit
) -> list[IngredientCustomization]:
    """Replace this user's entire ingredient overlay for this saved recipe
    with the submitted list. Wiping and rebuilding from scratch (rather than
    diffing row by row) is simplest and correct for a "Save" button that
    submits the whole edited list at once."""
    canonical_by_id = {ingredient.id: ingredient for ingredient in recipe.ingredients}

    db.query(IngredientCustomization).filter(
        IngredientCustomization.saved_recipe_id == saved_recipe.id
    ).delete()

    add_position = 0
    for item in payload.items:
        if item.ingredient_id is not None:
            canonical = canonical_by_id.get(item.ingredient_id)
            if canonical is None:
                continue  # not actually an ingredient of this recipe -- ignore
            unchanged = (
                item.quantity == canonical.quantity
                and item.unit == canonical.unit
                and item.name == canonical.name
            )
            if unchanged:
                continue  # matches canonical -- no overlay row needed
            db.add(
                IngredientCustomization(
                    saved_recipe_id=saved_recipe.id,
                    ingredient_id=item.ingredient_id,
                    action=CustomizationAction.MODIFY,
                    quantity=item.quantity,
                    unit=item.unit,
                    name=item.name,
                )
            )
        else:
            if not item.name.strip():
                continue  # skip blank added rows
            db.add(
                IngredientCustomization(
                    saved_recipe_id=saved_recipe.id,
                    ingredient_id=None,
                    action=CustomizationAction.ADD,
                    quantity=item.quantity,
                    unit=item.unit,
                    name=item.name,
                    position=add_position,
                )
            )
            add_position += 1

    for ingredient_id in payload.removed_ingredient_ids:
        if ingredient_id in canonical_by_id:
            db.add(
                IngredientCustomization(
                    saved_recipe_id=saved_recipe.id,
                    ingredient_id=ingredient_id,
                    action=CustomizationAction.REMOVE,
                )
            )

    db.commit()
    return (
        db.query(IngredientCustomization)
        .filter(IngredientCustomization.saved_recipe_id == saved_recipe.id)
        .all()
    )
