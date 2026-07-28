from sqlalchemy.orm import Session

from app.models.glossary_term import GlossaryTerm
from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.recipe_insight import RecipeInsight
from app.models.step import Step
from app.schemas.insight import GeneratedInsights
from app.schemas.recipe import ParsedRecipe


def persist_parsed_recipe(
    db: Session,
    parsed: ParsedRecipe,
    user_id: int,
    source_url: str | None = None,
    raw_source_text: str | None = None,
) -> Recipe:
    recipe = Recipe(
        title=parsed.title,
        servings=parsed.servings,
        prep_time=parsed.prep_time,
        cook_time=parsed.cook_time,
        total_time=parsed.total_time,
        equipment=parsed.equipment,
        source_url=source_url,
        raw_source_text=raw_source_text,
        created_by_user_id=user_id,
    )
    db.add(recipe)
    db.flush()  # assigns recipe.id without committing yet

    for position, ingredient in enumerate(parsed.ingredients):
        db.add(
            Ingredient(
                recipe_id=recipe.id,
                position=position,
                quantity=ingredient.quantity,
                unit=ingredient.unit,
                name=ingredient.name,
                notes=ingredient.notes,
                raw_text=ingredient.raw_text,
            )
        )

    for position, step in enumerate(parsed.steps):
        db.add(Step(recipe_id=recipe.id, position=position, instruction=step.instruction))

    db.commit()
    db.refresh(recipe)
    return recipe


def persist_recipe_insights(db: Session, recipe: Recipe, generated: GeneratedInsights) -> None:
    """Resolve Claude's generated insights against real glossary term rows
    and the recipe's own step/ingredient rows, then persist. Silently skips
    any insight tagging a glossary_term_slug that doesn't exist, or an
    anchor index out of range -- Claude's structured output is trusted for
    shape but not for referential correctness."""
    glossary_terms_by_slug = {t.slug: t for t in db.query(GlossaryTerm).all()}

    for position, insight in enumerate(generated.insights):
        term = glossary_terms_by_slug.get(insight.glossary_term_slug)
        if term is None:
            continue

        step_id = None
        ingredient_id = None
        if insight.anchor.type == "step" and insight.anchor.index is not None:
            if 0 <= insight.anchor.index < len(recipe.steps):
                step_id = recipe.steps[insight.anchor.index].id
        elif insight.anchor.type == "ingredient" and insight.anchor.index is not None:
            if 0 <= insight.anchor.index < len(recipe.ingredients):
                ingredient_id = recipe.ingredients[insight.anchor.index].id

        db.add(
            RecipeInsight(
                recipe_id=recipe.id,
                glossary_term_id=term.id,
                note=insight.note,
                step_id=step_id,
                ingredient_id=ingredient_id,
                position=position,
            )
        )
    db.commit()
