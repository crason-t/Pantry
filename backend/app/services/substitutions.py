from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.schemas.substitution import SubstitutionSuggestions
from app.services.claude_client import get_claude_client, get_model

SUBSTITUTION_PROMPT_TEMPLATE = """You are a knowledgeable home cook helping someone who doesn't have one of the ingredients for a recipe.

Recipe: {title}

Full ingredient list, for context on how things are used together:
{ingredients_context}

Steps:
{steps_context}

The user is missing this ingredient and wants substitute options:
{target_ingredient}

Suggest 2-4 reasonable substitutes for just this one ingredient, in the context of this specific recipe -- think about the role it plays here (flavor, texture, binding, leavening, moisture, etc.), not just a generic pantry swap list. Order suggestions from most to least recommended. For each suggestion:
- substitute: the substitute itself, with a rough quantity adjustment when it differs from the original (e.g. "1/2 cup buttermilk + 1/2 tsp baking soda" or "2 tbsp olive oil"). Keep it short.
- reason: one short sentence on why it works here, specific to this recipe when possible.

If nothing reasonable substitutes (rare -- e.g. the ingredient the dish is named after), return your most honest best-effort options rather than an empty list.
"""


def generate_ingredient_substitutions(recipe: Recipe, ingredient: Ingredient) -> SubstitutionSuggestions:
    """On-demand only -- never persisted. Called fresh each time a user asks,
    per docs/MVP.md's data model summary."""
    ingredients_context = "\n".join(f"- {ing.raw_text}" for ing in recipe.ingredients)
    steps_context = "\n".join(f"{i}. {step.instruction}" for i, step in enumerate(recipe.steps, start=1))

    prompt = SUBSTITUTION_PROMPT_TEMPLATE.format(
        title=recipe.title,
        ingredients_context=ingredients_context,
        steps_context=steps_context,
        target_ingredient=ingredient.raw_text,
    )

    client = get_claude_client()
    response = client.messages.parse(
        model=get_model(),
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        output_format=SubstitutionSuggestions,
    )
    return response.parsed_output
