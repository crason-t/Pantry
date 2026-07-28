from pydantic import BaseModel


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
