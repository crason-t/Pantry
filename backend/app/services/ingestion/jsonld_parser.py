import json
import re
from typing import Any

from bs4 import BeautifulSoup

from app.schemas.recipe import ParsedIngredient, ParsedRecipe, ParsedStep

_DURATION_RE = re.compile(r"P(?:\d+D)?T(?:(\d+)H)?(?:(\d+)M)?")


def _iso8601_duration_to_human(duration: str | None) -> str | None:
    if not duration:
        return None
    match = _DURATION_RE.match(duration)
    if not match:
        return duration
    hours, minutes = match.groups()
    parts = []
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else duration


def _find_recipe_node(data: Any) -> dict | None:
    if isinstance(data, dict):
        types = data.get("@type")
        types = [types] if isinstance(types, str) else (types or [])
        if "Recipe" in types:
            return data
        if "@graph" in data:
            return _find_recipe_node(data["@graph"])
    elif isinstance(data, list):
        for item in data:
            found = _find_recipe_node(item)
            if found:
                return found
    return None


def _instruction_texts(instructions: Any) -> list[str]:
    if isinstance(instructions, str):
        return [line.strip() for line in instructions.split("\n") if line.strip()]
    texts: list[str] = []
    if isinstance(instructions, list):
        for item in instructions:
            if isinstance(item, str):
                texts.append(item)
            elif isinstance(item, dict):
                if item.get("@type") == "HowToSection" and "itemListElement" in item:
                    texts.extend(_instruction_texts(item["itemListElement"]))
                elif "text" in item:
                    texts.append(item["text"])
    return texts


def _parse_servings(node: dict) -> int | None:
    value = node.get("recipeYield")
    if isinstance(value, list):
        value = value[0] if value else None
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        match = re.search(r"\d+", value)
        if match:
            return int(match.group())
    return None


def parse_jsonld_recipe(html: str) -> ParsedRecipe | None:
    """Scan <script type="application/ld+json"> blocks for a schema.org
    Recipe node. Returns None if no usable Recipe data is found -- the
    caller should fall back to Claude extraction in that case."""
    soup = BeautifulSoup(html, "html.parser")
    for script in soup.find_all("script", type="application/ld+json"):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except json.JSONDecodeError:
            continue

        node = _find_recipe_node(data)
        if node is None or not node.get("name"):
            continue

        raw_ingredients = node.get("recipeIngredient") or node.get("ingredients") or []
        ingredients = [
            ParsedIngredient(name=text, raw_text=text)
            for text in raw_ingredients
            if isinstance(text, str)
        ]

        steps = [ParsedStep(instruction=text) for text in _instruction_texts(node.get("recipeInstructions"))]

        return ParsedRecipe(
            title=node["name"],
            servings=_parse_servings(node),
            prep_time=_iso8601_duration_to_human(node.get("prepTime")),
            cook_time=_iso8601_duration_to_human(node.get("cookTime")),
            total_time=_iso8601_duration_to_human(node.get("totalTime")),
            equipment=[],
            ingredients=ingredients,
            steps=steps,
        )
    return None
