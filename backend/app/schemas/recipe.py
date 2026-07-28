from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.insight import RecipeInsightRead


class ParsedIngredient(BaseModel):
    quantity: str | None = None
    unit: str | None = None
    name: str
    notes: str | None = None
    raw_text: str


class ParsedStep(BaseModel):
    instruction: str


class ParsedRecipe(BaseModel):
    """The common shape both ingestion paths (JSON-LD, Claude extraction)
    converge on before persistence -- see docs/MVP.md."""

    title: str
    servings: int | None = None
    prep_time: str | None = None
    cook_time: str | None = None
    total_time: str | None = None
    equipment: list[str] = []
    ingredients: list[ParsedIngredient]
    steps: list[ParsedStep]


class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    quantity: str | None
    unit: str | None
    name: str
    notes: str | None
    raw_text: str


class StepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    position: int
    instruction: str


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    servings: int | None
    prep_time: str | None
    cook_time: str | None
    total_time: str | None
    equipment: list[str]
    source_url: str | None
    created_by_user_id: int
    created_at: datetime
    ingredients: list[IngredientRead]
    steps: list[StepRead]
    insights: list[RecipeInsightRead]


class RecipeSummary(BaseModel):
    """Lightweight shape for cookbook list views -- no ingredients/steps."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    servings: int | None
    total_time: str | None
    saved_at: datetime
