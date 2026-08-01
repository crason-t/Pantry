import logging

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.models.recipe import Recipe
from app.models.recipe_insight import RecipeInsight
from app.models.saved_recipe import SavedRecipe
from app.models.user import User
from app.schemas.recipe import RecipeRead, RecipeSummary, RecommendationSummary
from app.schemas.substitution import SubstitutionSuggestions
from app.services.ingestion.pipeline import ingest_from_text, ingest_from_url
from app.services.insights import generate_recipe_insights
from app.services.recipes import persist_parsed_recipe, persist_generated_recipe_content
from app.services.recommendations import (
    generate_recipe_recommendation,
    generate_recipe_recommendation_batch,
)
from app.services.substitutions import generate_ingredient_substitutions

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recipes", tags=["recipes"])


class IngestRequest(BaseModel):
    url: str | None = None
    text: str | None = None


def _get_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = (
        db.query(Recipe)
        .options(
            selectinload(Recipe.ingredients),
            selectinload(Recipe.steps),
            selectinload(Recipe.insights).selectinload(RecipeInsight.glossary_term),
            selectinload(Recipe.tips),
        )
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


@router.post("/ingest", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def ingest_recipe(
    payload: IngestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Recipe:
    if payload.url:
        parsed = ingest_from_url(payload.url)
        recipe = persist_parsed_recipe(db, parsed, current_user.id, source_url=payload.url)
    elif payload.text:
        parsed = ingest_from_text(payload.text)
        recipe = persist_parsed_recipe(db, parsed, current_user.id, raw_source_text=payload.text)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide either url or text")

    try:
        generated = generate_recipe_insights(db, recipe)
        persist_generated_recipe_content(db, recipe, generated)
    except Exception:
        # Best-effort: insight generation is a nice-to-have. A Claude/parsing
        # failure here shouldn't fail the whole ingestion -- the recipe is
        # already persisted and usable without its insights.
        logger.exception("Insight generation failed for recipe %s", recipe.id)

    return _get_recipe_or_404(db, recipe.id)


@router.get("/cookbook", response_model=list[RecipeSummary])
def list_cookbook(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    rows = (
        db.query(SavedRecipe, Recipe)
        .join(Recipe, Recipe.id == SavedRecipe.recipe_id)
        .filter(SavedRecipe.user_id == current_user.id)
        .order_by(SavedRecipe.saved_at.desc())
        .all()
    )
    return [
        {
            "id": recipe.id,
            "title": recipe.title,
            "servings": recipe.servings,
            "total_time": recipe.total_time,
            "saved_at": saved.saved_at,
        }
        for saved, recipe in rows
    ]


_EMPTY_COOKBOOK_DETAIL = (
    "Save a few recipes to your cookbook first — recommendations are based on what you've saved."
)


def _load_cookbook_recipes_or_400(db: Session, user_id: int) -> list[Recipe]:
    """The user's saved recipes with ingredients eagerly loaded (the taste
    context recommendation prompts are built from); 400 if the cookbook is
    empty."""
    cookbook_recipes = (
        db.query(Recipe)
        .join(SavedRecipe, SavedRecipe.recipe_id == Recipe.id)
        .options(selectinload(Recipe.ingredients))
        .filter(SavedRecipe.user_id == user_id)
        .order_by(SavedRecipe.saved_at.desc())
        .all()
    )
    if not cookbook_recipes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=_EMPTY_COOKBOOK_DETAIL)
    return cookbook_recipes


def _persist_recommendation(db: Session, parsed, user_id: int) -> Recipe:
    """Persist one generated recipe plus the same best-effort insights block
    /ingest uses."""
    recipe = persist_parsed_recipe(db, parsed, user_id, is_recommendation=True)
    try:
        generated = generate_recipe_insights(db, recipe)
        persist_generated_recipe_content(db, recipe, generated)
    except Exception:
        # Best-effort: insight generation is a nice-to-have. A Claude/parsing
        # failure here shouldn't fail the whole recommendation -- the recipe
        # is already persisted and usable without its insights.
        logger.exception("Insight generation failed for recipe %s", recipe.id)
    return recipe


@router.post("/recommend", response_model=RecipeRead, status_code=status.HTTP_201_CREATED)
def recommend_recipe(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Recipe:
    # No request body -- the recommendation is driven entirely by the user's
    # saved cookbook. (Declaring no body param also means an empty `{}` body
    # from the client is simply ignored.)
    cookbook_recipes = _load_cookbook_recipes_or_400(db, current_user.id)

    try:
        parsed = generate_recipe_recommendation(cookbook_recipes)
    except Exception:
        logger.exception("Recipe recommendation failed for user %s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate a recommendation right now",
        )

    recipe = _persist_recommendation(db, parsed, current_user.id)
    return _get_recipe_or_404(db, recipe.id)


@router.get("/recommendations", response_model=list[RecommendationSummary])
def list_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Recipe]:
    return (
        db.query(Recipe)
        .filter(Recipe.created_by_user_id == current_user.id, Recipe.is_recommendation.is_(True))
        .order_by(Recipe.created_at.desc(), Recipe.id.desc())
        .limit(3)
        .all()
    )


@router.post(
    "/recommendations", response_model=list[RecommendationSummary], status_code=status.HTTP_201_CREATED
)
def create_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Recipe]:
    cookbook_recipes = _load_cookbook_recipes_or_400(db, current_user.id)

    try:
        parsed_batch = generate_recipe_recommendation_batch(cookbook_recipes)
    except Exception:
        logger.exception("Recipe recommendation batch failed for user %s", current_user.id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not generate recommendations right now",
        )

    # The prompt asks for exactly 3, but cap defensively -- Claude's output
    # shape is validated, not its count.
    return [_persist_recommendation(db, parsed, current_user.id) for parsed in parsed_batch[:3]]


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Recipe:
    return _get_recipe_or_404(db, recipe_id)


@router.post("/{recipe_id}/save", status_code=status.HTTP_204_NO_CONTENT)
def save_recipe(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    _get_recipe_or_404(db, recipe_id)  # 404s if the recipe doesn't exist
    existing = (
        db.query(SavedRecipe)
        .filter(SavedRecipe.user_id == current_user.id, SavedRecipe.recipe_id == recipe_id)
        .first()
    )
    if existing is not None:
        return  # idempotent: already saved
    db.add(SavedRecipe(user_id=current_user.id, recipe_id=recipe_id))
    db.commit()


@router.post(
    "/{recipe_id}/ingredients/{ingredient_id}/substitutions",
    response_model=SubstitutionSuggestions,
)
def get_ingredient_substitutions(
    recipe_id: int,
    ingredient_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SubstitutionSuggestions:
    recipe = _get_recipe_or_404(db, recipe_id)
    ingredient = next((i for i in recipe.ingredients if i.id == ingredient_id), None)
    if ingredient is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found")

    # On-demand only, never persisted (see docs/MVP.md) -- a Claude failure
    # here should surface to the user, unlike best-effort ingestion insights.
    try:
        return generate_ingredient_substitutions(recipe, ingredient)
    except Exception:
        logger.exception(
            "Substitution generation failed for recipe %s ingredient %s", recipe_id, ingredient_id
        )
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Could not get substitution suggestions right now",
        )
