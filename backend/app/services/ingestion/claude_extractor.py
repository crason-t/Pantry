import logging

import anthropic

from app.schemas.recipe import ParsedRecipe
from app.services.claude_client import get_claude_client, get_model

logger = logging.getLogger(__name__)


class RecipeExtractionUnavailable(RuntimeError):
    """Extraction couldn't complete for a transient reason. Callers should
    surface a retry-able error rather than letting it become a 500."""


# Structured outputs compile ParsedRecipe into a decoding grammar server-side.
# That compile happens once per schema and is then cached ~24h, so the first
# extraction after an idle day (or after any ParsedRecipe/ParsedIngredient/
# ParsedStep edit) pays it and can exceed the API's time limit -- measured at
# 97s cold vs 5s warm. The API reports that as a 400, which the SDK does not
# retry, so we retry it once ourselves; the second attempt benefits from the
# compile work the first one already did.
_GRAMMAR_TIMEOUT_MARKER = "grammar compilation timed out"


def _is_grammar_compilation_timeout(err: anthropic.BadRequestError) -> bool:
    detail = f"{getattr(err, 'message', '') or ''} {err}".lower()
    return _GRAMMAR_TIMEOUT_MARKER in detail


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
    (no structured markup to check there).

    Raises RecipeExtractionUnavailable if a grammar-compilation timeout
    survives one retry. Every other API error propagates untouched.
    """
    client = get_claude_client()
    attempts = 2

    for attempt in range(1, attempts + 1):
        try:
            response = client.messages.parse(
                model=get_model(),
                max_tokens=4096,
                messages=[{"role": "user", "content": EXTRACTION_PROMPT + text}],
                output_format=ParsedRecipe,
            )
            return response.parsed_output
        except anthropic.BadRequestError as err:
            if not _is_grammar_compilation_timeout(err):
                raise
            if attempt == attempts:
                logger.warning(
                    "Recipe extraction gave up after %s grammar-compilation timeouts "
                    "(last request_id=%s)",
                    attempts,
                    getattr(err, "request_id", None),
                )
                raise RecipeExtractionUnavailable(
                    "Recipe extraction is warming up and timed out. Try again in a moment."
                ) from err
            logger.warning(
                "Grammar compilation timed out on attempt %s/%s (request_id=%s); retrying",
                attempt,
                attempts,
                getattr(err, "request_id", None),
            )

    # Unreachable: the loop either returns or raises.
    raise AssertionError("extract_recipe_with_claude exhausted its retry loop")
