from pydantic import BaseModel

from app.models.recipe import Recipe
from app.schemas.recipe import ParsedRecipe
from app.services.claude_client import get_claude_client, get_model

_TASTE_CONTEXT_TEMPLATE = """You are a thoughtful home-cooking companion. Below are the recipes a user has saved to their personal cookbook -- treat them as a picture of the user's tastes (cuisines, flavors, ingredients, and techniques they gravitate toward).

Saved recipes:
{cookbook_context}
"""

_RECIPE_SHAPE_INSTRUCTIONS = """Write each recipe as a complete, cookable recipe: title, servings, prep/cook/total time (short human strings like '15m' or '1h 30m', or null if not applicable), equipment needed, ingredients, and steps in order. Only set an ingredient's component when the recipe genuinely groups ingredients under sub-headings (e.g. 'Dressing', 'Crust'); otherwise leave component null -- don't invent a grouping.

For each ingredient, split out quantity/unit and also fill in colloquial_quantity: a natural, easy-to-visualize amount using everyday cooking language -- e.g. 'a spoonful', 'a handful', '1 head', '3 cherry tomatoes', 'to taste', 'for searing' -- rather than a precise weight. Use colloquial_quantity for whichever phrasing a home cook would actually picture; quantity/unit should hold the precise measurement (prefer grams or milliliters for solids/liquids when a reasonable conversion is derivable, otherwise the amount as you'd state it). If the ingredient is only ever expressed as a plain count or descriptor with no more precise weight available (e.g. '1 tortilla', '2 eggs', 'to taste'), put that in colloquial_quantity and leave quantity/unit null rather than duplicating it. Always fill in raw_text with the full ingredient line as it would appear in a written recipe."""

_SINGLE_TASK = """Invent ONE new recipe this user is likely to love, given those tastes. It must be complementary to the cookbook -- not a duplicate of, or a trivial variation on, anything already saved."""

_BATCH_TASK = """Invent exactly 3 distinct new recipes this user is likely to love, given those tastes. Each must be complementary to the cookbook -- not a duplicate of, or a trivial variation on, anything already saved -- and the 3 recipes must also be clearly distinct from and complementary to each other (don't propose three takes on the same dish or cuisine)."""


class RecommendedRecipeBatch(BaseModel):
    """Structured-output wrapper for a batch of invented recipes."""

    recipes: list[ParsedRecipe]


def _format_cookbook_context(cookbook_recipes: list[Recipe]) -> str:
    return "\n".join(
        f"- {recipe.title} (ingredients: {', '.join(ing.name for ing in recipe.ingredients)})"
        for recipe in cookbook_recipes
    )


def _build_prompt(cookbook_recipes: list[Recipe], task: str) -> str:
    return "\n".join(
        [
            _TASTE_CONTEXT_TEMPLATE.format(cookbook_context=_format_cookbook_context(cookbook_recipes)),
            task,
            "",
            _RECIPE_SHAPE_INSTRUCTIONS,
        ]
    )


def generate_recipe_recommendation(cookbook_recipes: list[Recipe]) -> ParsedRecipe:
    """Invent a brand-new recipe matched to the user's cookbook tastes.
    Returns the same ParsedRecipe shape the ingestion paths converge on, so
    the result persists exactly like an ingested recipe."""
    client = get_claude_client()
    response = client.messages.parse(
        model=get_model(),
        max_tokens=4096,
        messages=[{"role": "user", "content": _build_prompt(cookbook_recipes, _SINGLE_TASK)}],
        output_format=ParsedRecipe,
    )
    return response.parsed_output


def generate_recipe_recommendation_batch(cookbook_recipes: list[Recipe]) -> list[ParsedRecipe]:
    """One Claude call inventing 3 distinct recipes for the homepage
    recommendations section."""
    client = get_claude_client()
    response = client.messages.parse(
        model=get_model(),
        max_tokens=16384,
        messages=[{"role": "user", "content": _build_prompt(cookbook_recipes, _BATCH_TASK)}],
        output_format=RecommendedRecipeBatch,
    )
    return response.parsed_output.recipes
