from app.schemas.recipe import ParsedRecipe
from app.services.ingestion.claude_extractor import extract_recipe_with_claude
from app.services.ingestion.jsonld_parser import parse_jsonld_recipe
from app.services.ingestion.url_fetcher import fetch_html


def ingest_from_url(url: str) -> ParsedRecipe:
    html = fetch_html(url)
    parsed = parse_jsonld_recipe(html)
    if parsed is not None and parsed.ingredients and parsed.steps:
        return parsed
    return extract_recipe_with_claude(html)


def ingest_from_text(text: str) -> ParsedRecipe:
    return extract_recipe_with_claude(text)
