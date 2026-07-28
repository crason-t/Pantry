from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.recipe import ParsedRecipe
from app.services.ingestion.pipeline import ingest_from_text, ingest_from_url

router = APIRouter(prefix="/recipes", tags=["recipes"])


class IngestRequest(BaseModel):
    url: str | None = None
    text: str | None = None


@router.post("/ingest", response_model=ParsedRecipe)
def ingest_recipe(
    payload: IngestRequest,
    current_user: User = Depends(get_current_user),
) -> ParsedRecipe:
    """Placeholder: parses and returns a recipe, doesn't persist yet.
    Persistence lands with the cookbook vertical slice (see PROJECT_PLAN.md)."""
    if payload.url:
        return ingest_from_url(payload.url)
    if payload.text:
        return ingest_from_text(payload.text)
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provide either url or text")
