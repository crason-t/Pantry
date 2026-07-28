from app.schemas.recipe import ParsedRecipe
from app.services.claude_client import get_claude_client, get_model

EXTRACTION_PROMPT = (
    "Extract the recipe below into structured form: title, servings, "
    "prep/cook/total time (short human strings like '15m' or '1h 30m', or "
    "null if not stated), equipment mentioned, ingredients (with quantity, "
    "unit, and name split out where possible, plus the original raw_text), "
    "and steps in order. If this text is not a recipe, do your best to "
    "extract whatever structure is present.\n\n---\n\n"
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
