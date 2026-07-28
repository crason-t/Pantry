from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class SavedRecipe(Base):
    """Cookbook entry: which user saved which recipe."""

    __tablename__ = "saved_recipes"
    __table_args__ = (UniqueConstraint("user_id", "recipe_id", name="uq_saved_recipes_user_recipe"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    recipe_id: Mapped[int] = mapped_column(ForeignKey("recipes.id"))
    saved_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
