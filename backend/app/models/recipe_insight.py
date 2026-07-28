from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RecipeInsight(Base):
    """A "why this dish works" callout: tags a GlossaryTerm and adds a
    recipe-specific note, optionally anchored to a specific Step/Ingredient.
    Generated at ingestion time; unlike GlossaryTerm, this is per-recipe."""

    __tablename__ = "recipe_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    glossary_term_id: Mapped[int] = mapped_column(ForeignKey("glossary_terms.id"))
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    step_id: Mapped[int | None] = mapped_column(ForeignKey("steps.id"), nullable=True)
    ingredient_id: Mapped[int | None] = mapped_column(ForeignKey("ingredients.id"), nullable=True)
    position: Mapped[int] = mapped_column(Integer)

    recipe: Mapped["Recipe"] = relationship(back_populates="insights")
    glossary_term: Mapped["GlossaryTerm"] = relationship(back_populates="insights")
