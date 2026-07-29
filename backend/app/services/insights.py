from sqlalchemy.orm import Session

from app.models.glossary_term import GlossaryTerm
from app.models.recipe import Recipe
from app.schemas.insight import GeneratedInsights
from app.services.claude_client import get_claude_client, get_model

INSIGHT_PROMPT_TEMPLATE = """You are a culinary expert annotating a recipe with brief "why this dish works" insights.

Recipe: {title}

Ingredients (0-indexed):
{ingredients_context}

Steps (0-indexed):
{steps_context}

Available glossary terms -- only use these exact slugs, never invent a new one:
{glossary_context}

Produce two kinds of output:

1. INSIGHTS: For each ingredient or step where a technique, food-science \
reaction, or flavor element meaningfully explains why the dish works, generate \
an insight: tag one glossary term slug from the list above, and write a short \
(1-2 sentence) recipe-specific note explaining why it matters *here*, in this \
recipe -- not a generic definition of the term (the reader already has that). \
Anchor most insights to the specific step or ingredient they're about via its \
index. Reserve anchor type "general" for only the 2-4 truly major, dish-defining \
aspects of the recipe as a whole (the ones a home cook most needs to understand \
to get the dish right) -- these render as separate "why this dish works" cards, \
so keep this list short and restrict it to what actually matters, not a general \
observation for every recipe. A "general" note can call out a common mistake \
people make with this dish and why it happens, when that's the most useful \
framing.

Only generate insights for genuinely meaningful moments, not every ingredient or \
step. Aim for roughly 3-6 insights total for a typical recipe. If nothing in the \
provided glossary terms meaningfully applies, return an empty list rather than \
forcing a weak match.

2. TIPS: Identify the 2-4 most crucial, must-get-right pointers for this \
specific recipe -- the handful of things that, if done wrong, will keep it from \
turning out the way it should (e.g. a temperature, timing, or technique detail; \
a step that's easy to rush or skip). Write each as a short, direct, actionable \
sentence a cook would want to read *before* starting, not a restatement of a \
step. Only include tips that are genuinely make-or-break for this recipe -- \
fewer, sharper tips beat a long list of minor reminders.
"""


def generate_recipe_insights(db: Session, recipe: Recipe) -> GeneratedInsights:
    glossary_terms = db.query(GlossaryTerm).order_by(GlossaryTerm.category, GlossaryTerm.slug).all()
    glossary_context = "\n".join(f"- {t.slug} ({t.category.value}): {t.definition}" for t in glossary_terms)
    ingredients_context = "\n".join(f"{i}. {ing.raw_text}" for i, ing in enumerate(recipe.ingredients))
    steps_context = "\n".join(f"{i}. {step.instruction}" for i, step in enumerate(recipe.steps))

    prompt = INSIGHT_PROMPT_TEMPLATE.format(
        title=recipe.title,
        ingredients_context=ingredients_context,
        steps_context=steps_context,
        glossary_context=glossary_context,
    )

    client = get_claude_client()
    response = client.messages.parse(
        model=get_model(),
        max_tokens=3072,
        messages=[{"role": "user", "content": prompt}],
        output_format=GeneratedInsights,
    )
    return response.parsed_output
