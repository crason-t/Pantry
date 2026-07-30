from pydantic import BaseModel, ConfigDict


class MergedIngredientRead(BaseModel):
    """One row of a recipe's ingredient list after this user's overlay has
    been applied -- see services/ingredient_customizations.py. Shaped like
    IngredientRead plus the fields the frontend needs to tell canonical rows
    apart from this user's own additions/edits."""

    model_config = ConfigDict(from_attributes=True)

    ingredient_id: int | None  # canonical Ingredient.id; null for a user-added line
    customization_id: int | None  # IngredientCustomization.id backing this row, if any
    position: int
    quantity: str | None
    unit: str | None
    colloquial_quantity: str | None
    name: str
    component: str | None
    notes: str | None
    raw_text: str
    is_custom: bool  # True for a line the user added themselves (no canonical row)


class CustomizedIngredientsRead(BaseModel):
    is_saved: bool  # whether the current user has this recipe in their cookbook
    ingredients: list[MergedIngredientRead]


class IngredientEdit(BaseModel):
    """One row of the edited ingredient list, as submitted on Save.
    ingredient_id set => edits an existing canonical ingredient (a MODIFY
    overlay). ingredient_id None => a brand-new line (an ADD overlay)."""

    ingredient_id: int | None = None
    quantity: str | None = None
    unit: str | None = None
    name: str


class IngredientListEdit(BaseModel):
    items: list[IngredientEdit]
    removed_ingredient_ids: list[int] = []
