from typing import Literal

from pydantic import BaseModel, ConfigDict


class InsightAnchor(BaseModel):
    """Where a generated insight attaches: a specific step, a specific
    ingredient, or nowhere in particular (a general note about the dish)."""

    type: Literal["step", "ingredient", "general"]
    index: int | None = None  # 0-based index into steps/ingredients; unused for "general"


class GeneratedInsight(BaseModel):
    """One "why this works" callout, as Claude produces it -- before it's
    resolved against real glossary term/step/ingredient rows."""

    glossary_term_slug: str
    note: str
    anchor: InsightAnchor


class GeneratedInsights(BaseModel):
    insights: list[GeneratedInsight]
    tips: list[str] = []


class GlossaryTermRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    slug: str
    category: str
    name: str
    definition: str


class RecipeInsightRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    glossary_term: GlossaryTermRead
    note: str | None
    step_id: int | None
    ingredient_id: int | None
    position: int


class RecipeTipRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    tip_text: str
