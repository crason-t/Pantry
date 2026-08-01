from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(500))
    servings: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prep_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    cook_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    total_time: Mapped[str | None] = mapped_column(String(50), nullable=True)
    equipment: Mapped[list[str]] = mapped_column(JSONB, default=list)
    source_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_source_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    is_recommendation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    ingredients: Mapped[list["Ingredient"]] = relationship(
        back_populates="recipe", order_by="Ingredient.position", cascade="all, delete-orphan"
    )
    steps: Mapped[list["Step"]] = relationship(
        back_populates="recipe", order_by="Step.position", cascade="all, delete-orphan"
    )
    insights: Mapped[list["RecipeInsight"]] = relationship(
        back_populates="recipe", order_by="RecipeInsight.position", cascade="all, delete-orphan"
    )
    tips: Mapped[list["RecipeTip"]] = relationship(
        back_populates="recipe", order_by="RecipeTip.position", cascade="all, delete-orphan"
    )
