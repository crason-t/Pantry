from app.schemas.recipe import ParsedRecipe
from app.services.claude_client import get_claude_client, get_model

EXTRACTION_PROMPT = (
    "Extract the recipe below into structured form: title, servings, "
    "prep/cook/total time (short human strings like '15m' or '1h 30m', or "
    "null if not stated), equipment mentioned, ingredients, and steps in "
    "order. If the recipe groups its ingredients under sub-headings (e.g. "
    "'For the dressing', 'Filling', 'Crust'), set each ingredient's "
    "component to that group's short label (e.g. 'Dressing'); otherwise "
    "leave component null -- don't invent a grouping that isn't in the "
    "source.\n\n"
    "For each ingredient, split out quantity/unit and also fill in "
    "colloquial_quantity: a natural, easy-to-visualize amount using "
    "everyday cooking language -- e.g. 'a spoonful', 'a handful', '1 head', "
    "'3 cherry tomatoes', 'to taste', 'for searing' -- rather than a "
    "precise weight. Use colloquial_quantity for whichever phrasing a home "
    "cook would actually picture; quantity/unit should hold the precise "
    "measurement (prefer converting solids/liquids to grams or milliliters "
    "when a reasonable conversion is derivable, otherwise keep the amount "
    "as stated). If the ingredient is only ever expressed as a plain count "
    "or descriptor with no more precise weight available (e.g. '1 tortilla', "
    "'2 eggs', 'to taste'), put that in colloquial_quantity and leave "
    "quantity/unit null rather than duplicating it. Always include the "
    "original raw_text.\n\n"
    "If this text is not a recipe, do your best to extract whatever "
    "structure is present.\n\n---\n\n"
)


def extract_recipe_with_claude(text: str) -> ParsedRecipe:
    """Structured-output extraction -- used as the URL-ingestion fallback
    when JSON-LD is absent/incomplete, and unconditionally for pasted text
    (no structured markup to check there)."""
    client = get_claude_client()
    response = client.messages.parse(
        model=get_model(),
        max_tokens=4096,
        messages=[{"role": "user", "content": EXTRACTION_PROMPT + text}],
        output_format=ParsedRecipe,
    )
    return response.parsed_output
