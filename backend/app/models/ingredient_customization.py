import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class CustomizationAction(str, enum.Enum):
    MODIFY = "modify"  # overrides quantity/unit/name of a canonical ingredient
    REMOVE = "remove"  # hides a canonical ingredient from this user's view
    ADD = "add"  # a brand-new line with no canonical counterpart


class IngredientCustomization(Base):
    """Per-user overlay on top of a recipe's canonical Ingredient rows.

    Recipe/Ingredient rows are shared canonical data, populated once at
    ingestion time -- the same Recipe can be saved by many users via
    SavedRecipe (unique(user_id, recipe_id)). Editing a user's copy of an
    ingredient must NEVER mutate the canonical Ingredient row, or it would
    silently change what every other user who saved this recipe sees.
    Instead, every add/modify/remove is recorded here, scoped to one
    SavedRecipe (one user's one save of one recipe), and merged with the
    canonical ingredients at read time -- see
    services/ingredient_customizations.py.

    - action=MODIFY: ingredient_id points at the canonical row being
      overridden. quantity/unit/name carry the full edited values (not a
      sparse diff -- the frontend always submits the complete edited row on
      save, so there's no ambiguity about which fields actually changed).
    - action=REMOVE: ingredient_id points at the canonical row to hide from
      this user's view. quantity/unit/name are unused.
    - action=ADD: ingredient_id is null (there's no canonical row to point
      at). name is required; quantity/unit are optional; position controls
      ordering among a user's own added lines.
    """

    __tablename__ = "ingredient_customizations"
    __table_args__ = (
        UniqueConstraint(
            "saved_recipe_id", "ingredient_id", name="uq_ingredient_customizations_saved_recipe_ingredient"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    saved_recipe_id: Mapped[int] = mapped_column(ForeignKey("saved_recipes.id"))
    ingredient_id: Mapped[int | None] = mapped_column(ForeignKey("ingredients.id"), nullable=True)
    action: Mapped[CustomizationAction] = mapped_column(Enum(CustomizationAction, name="customization_action"))
    quantity: Mapped[str | None] = mapped_column(String(50), nullable=True)
    unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    position: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
