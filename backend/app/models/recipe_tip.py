from sqlalchemy import ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class RecipeTip(Base):
    """A crucial, must-get-right pointer for a recipe -- generated at
    ingestion time alongside RecipeInsight, but distinct: a tip is
    actionable/imperative dish-level guidance, not a glossary-term callout."""

    __tablename__ = "recipe_tips"

    id: Mapped[int] = mapped_column(primary_key=True)
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    position: Mapped[int] = mapped_column(Integer)
    tip_text: Mapped[str] = mapped_column(Text)

    recipe: Mapped["Recipe"] = relationship(back_populates="tips")
