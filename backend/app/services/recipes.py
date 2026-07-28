from sqlalchemy.orm import Session

from app.models.ingredient import Ingredient
from app.models.recipe import Recipe
from app.models.step import Step
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
