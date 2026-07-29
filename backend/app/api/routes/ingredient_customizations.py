from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user, get_db
from app.models.ingredient_customization import IngredientCustomization
from app.models.recipe import Recipe
from app.models.saved_recipe import SavedRecipe
from app.models.user import User
from app.schemas.ingredient_customization import CustomizedIngredientsRead, IngredientListEdit
from app.services.ingredient_customizations import merge_ingredients, save_ingredient_customizations

router = APIRouter(prefix="/recipes", tags=["ingredient-customizations"])


def _get_recipe_or_404(db: Session, recipe_id: int) -> Recipe:
    recipe = (
        db.query(Recipe)
        .options(selectinload(Recipe.ingredients))
        .filter(Recipe.id == recipe_id)
        .first()
    )
    if recipe is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found")
    return recipe


def _get_saved_recipe(db: Session, user_id: int, recipe_id: int) -> SavedRecipe | None:
    return (
        db.query(SavedRecipe)
        .filter(SavedRecipe.user_id == user_id, SavedRecipe.recipe_id == recipe_id)
        .first()
    )


@router.get("/{recipe_id}/ingredients/customized", response_model=CustomizedIngredientsRead)
def get_customized_ingredients(
    recipe_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomizedIngredientsRead:
    recipe = _get_recipe_or_404(db, recipe_id)
    saved_recipe = _get_saved_recipe(db, current_user.id, recipe_id)
    if saved_recipe is None:
        # Nothing to scope an overlay to yet -- report the canonical
        # ingredients as-is and let the frontend know customization isn't
        # available until the recipe is saved.
        return CustomizedIngredientsRead(is_saved=False, ingredients=merge_ingredients(recipe, []))

    customizations = (
        db.query(IngredientCustomization)
        .filter(IngredientCustomization.saved_recipe_id == saved_recipe.id)
        .all()
    )
    return CustomizedIngredientsRead(is_saved=True, ingredients=merge_ingredients(recipe, customizations))


@router.put("/{recipe_id}/ingredients/customized", response_model=CustomizedIngredientsRead)
def put_customized_ingredients(
    recipe_id: int,
    payload: IngredientListEdit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CustomizedIngredientsRead:
    recipe = _get_recipe_or_404(db, recipe_id)
    saved_recipe = _get_saved_recipe(db, current_user.id, recipe_id)
    if saved_recipe is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Save this recipe to your cookbook before customizing its ingredients",
        )

    customizations = save_ingredient_customizations(db, saved_recipe, recipe, payload)
    return CustomizedIngredientsRead(is_saved=True, ingredients=merge_ingredients(recipe, customizations))
