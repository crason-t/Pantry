"""Tests for schema.org JSON-LD recipe extraction.

This is the no-LLM half of URL ingestion: when it succeeds the pipeline skips
the Claude call entirely, so its edge cases (recipe sites nest their markup in
wildly different ways) directly control cost and latency.
"""

import json

import pytest

from app.services.ingestion.jsonld_parser import parse_jsonld_recipe


def html_with_jsonld(payload) -> str:
    """Wrap a JSON-LD payload in the minimal page shape the parser scans."""
    return (
        "<html><head>"
        f'<script type="application/ld+json">{json.dumps(payload)}</script>'
        "</head><body><p>Not the recipe.</p></body></html>"
    )


COMPLETE_RECIPE = {
    "@context": "https://schema.org",
    "@type": "Recipe",
    "name": "Sheet-Pan Chicken Thighs",
    "recipeYield": "4 servings",
    "prepTime": "PT15M",
    "cookTime": "PT45M",
    "totalTime": "PT1H",
    "recipeIngredient": [
        "6 bone-in chicken thighs",
        "2 tbsp olive oil",
        "1 tsp smoked paprika",
    ],
    "recipeInstructions": [
        {"@type": "HowToStep", "text": "Heat the oven to 425F."},
        {"@type": "HowToStep", "text": "Toss the thighs with oil and paprika."},
        {"@type": "HowToStep", "text": "Roast 45 minutes until the skin crisps."},
    ],
}


class TestWellFormedRecipe:
    def test_parses_all_top_level_fields(self):
        recipe = parse_jsonld_recipe(html_with_jsonld(COMPLETE_RECIPE))

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"
        assert recipe.servings == 4
        assert recipe.prep_time == "15m"
        assert recipe.cook_time == "45m"
        assert recipe.total_time == "1h"

    def test_maps_ingredients_preserving_raw_text(self):
        recipe = parse_jsonld_recipe(html_with_jsonld(COMPLETE_RECIPE))

        assert [i.name for i in recipe.ingredients] == [
            "6 bone-in chicken thighs",
            "2 tbsp olive oil",
            "1 tsp smoked paprika",
        ]
        # JSON-LD gives one unsplit string, so raw_text mirrors name and the
        # quantity/unit split is left for downstream (Claude) enrichment.
        assert all(i.raw_text == i.name for i in recipe.ingredients)
        assert all(i.quantity is None and i.unit is None for i in recipe.ingredients)

    def test_maps_steps_in_source_order(self):
        recipe = parse_jsonld_recipe(html_with_jsonld(COMPLETE_RECIPE))

        assert [s.instruction for s in recipe.steps] == [
            "Heat the oven to 425F.",
            "Toss the thighs with oil and paprika.",
            "Roast 45 minutes until the skin crisps.",
        ]

    def test_equipment_is_empty_because_jsonld_does_not_carry_it(self):
        recipe = parse_jsonld_recipe(html_with_jsonld(COMPLETE_RECIPE))

        assert recipe.equipment == []


class TestRecipeNodeDiscovery:
    def test_finds_recipe_inside_graph_wrapper(self):
        payload = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "WebSite", "name": "A Food Blog"},
                {"@type": "Person", "name": "The Author"},
                COMPLETE_RECIPE,
            ],
        }

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"

    def test_finds_recipe_in_top_level_list(self):
        payload = [{"@type": "Organization", "name": "A Food Blog"}, COMPLETE_RECIPE]

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"

    def test_matches_when_type_is_a_list(self):
        payload = dict(COMPLETE_RECIPE, **{"@type": ["Article", "Recipe"]})

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"

    def test_skips_earlier_blocks_that_hold_no_recipe(self):
        html = (
            "<html><head>"
            '<script type="application/ld+json">'
            f'{json.dumps({"@type": "BreadcrumbList", "itemListElement": []})}'
            "</script>"
            f'<script type="application/ld+json">{json.dumps(COMPLETE_RECIPE)}</script>'
            "</head></html>"
        )

        recipe = parse_jsonld_recipe(html)

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"

    def test_recovers_when_an_earlier_block_is_malformed_json(self):
        html = (
            "<html><head>"
            '<script type="application/ld+json">{"@type": "Recipe", oops]</script>'
            f'<script type="application/ld+json">{json.dumps(COMPLETE_RECIPE)}</script>'
            "</head></html>"
        )

        recipe = parse_jsonld_recipe(html)

        assert recipe is not None
        assert recipe.title == "Sheet-Pan Chicken Thighs"


class TestNoUsableRecipe:
    def test_returns_none_when_page_has_no_jsonld_at_all(self):
        assert parse_jsonld_recipe("<html><body><h1>A recipe, in prose.</h1></body></html>") is None

    def test_returns_none_when_jsonld_holds_no_recipe_node(self):
        payload = {"@context": "https://schema.org", "@type": "Article", "name": "Not a recipe"}

        assert parse_jsonld_recipe(html_with_jsonld(payload)) is None

    def test_returns_none_when_recipe_node_has_no_name(self):
        # A nameless Recipe can't populate the required `title`, so it's
        # treated as unusable rather than raising.
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "name"}

        assert parse_jsonld_recipe(html_with_jsonld(payload)) is None

    def test_returns_none_when_every_block_is_malformed(self):
        html = '<html><head><script type="application/ld+json">{not json at all</script></head></html>'

        assert parse_jsonld_recipe(html) is None

    def test_returns_none_for_empty_script_block(self):
        assert parse_jsonld_recipe('<html><script type="application/ld+json"></script></html>') is None

    def test_ignores_jsonld_in_a_script_of_the_wrong_type(self):
        html = f'<html><script type="application/json">{json.dumps(COMPLETE_RECIPE)}</script></html>'

        assert parse_jsonld_recipe(html) is None


class TestInstructionShapes:
    def test_plain_string_splits_on_newlines_and_drops_blanks(self):
        payload = dict(COMPLETE_RECIPE, recipeInstructions="Preheat.\n\n  Roast.  \nRest.\n")

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert [s.instruction for s in recipe.steps] == ["Preheat.", "Roast.", "Rest."]

    def test_list_of_bare_strings(self):
        payload = dict(COMPLETE_RECIPE, recipeInstructions=["Preheat.", "Roast."])

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert [s.instruction for s in recipe.steps] == ["Preheat.", "Roast."]

    def test_flattens_howtosection_groups(self):
        payload = dict(
            COMPLETE_RECIPE,
            recipeInstructions=[
                {
                    "@type": "HowToSection",
                    "name": "For the chicken",
                    "itemListElement": [
                        {"@type": "HowToStep", "text": "Season the thighs."},
                        {"@type": "HowToStep", "text": "Roast them."},
                    ],
                },
                {
                    "@type": "HowToSection",
                    "name": "For the sauce",
                    "itemListElement": [{"@type": "HowToStep", "text": "Whisk the pan drippings."}],
                },
            ],
        )

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert [s.instruction for s in recipe.steps] == [
            "Season the thighs.",
            "Roast them.",
            "Whisk the pan drippings.",
        ]

    def test_missing_instructions_yields_no_steps(self):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeInstructions"}

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe is not None
        assert recipe.steps == []


class TestIngredientShapes:
    def test_falls_back_to_legacy_ingredients_key(self):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeIngredient"}
        payload["ingredients"] = ["1 cup rice", "2 cups stock"]

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert [i.name for i in recipe.ingredients] == ["1 cup rice", "2 cups stock"]

    def test_drops_non_string_entries(self):
        payload = dict(COMPLETE_RECIPE, recipeIngredient=["1 cup rice", {"name": "stock"}, None, "salt"])

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert [i.name for i in recipe.ingredients] == ["1 cup rice", "salt"]

    def test_missing_ingredients_yields_empty_list(self):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeIngredient"}

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe is not None
        assert recipe.ingredients == []


class TestServings:
    @pytest.mark.parametrize(
        "recipe_yield,expected",
        [
            (4, 4),
            ("4", 4),
            ("4 servings", 4),
            ("Serves 6", 6),
            ("6 to 8 servings", 6),
            (["8 servings", "8"], 8),
            ("a crowd", None),
            ([], None),
            (None, None),
        ],
    )
    def test_parses_yield_variants(self, recipe_yield, expected):
        payload = dict(COMPLETE_RECIPE, recipeYield=recipe_yield)

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe.servings == expected

    def test_missing_yield_is_none(self):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeYield"}

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe.servings is None


class TestDurations:
    @pytest.mark.parametrize(
        "iso,expected",
        [
            ("PT15M", "15m"),
            ("PT2H", "2h"),
            ("PT1H30M", "1h 30m"),
            ("P0DT1H15M", "1h 15m"),
            # No hour/minute component to render -- fall back to the raw value
            # rather than emitting an empty string.
            ("PT30S", "PT30S"),
            # Not an ISO-8601 duration at all: pass it through untouched.
            ("about 20 minutes", "about 20 minutes"),
        ],
    )
    def test_converts_iso_durations_to_human_strings(self, iso, expected):
        payload = dict(COMPLETE_RECIPE, prepTime=iso)

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe.prep_time == expected

    def test_missing_durations_are_none(self):
        payload = {
            k: v for k, v in COMPLETE_RECIPE.items() if k not in {"prepTime", "cookTime", "totalTime"}
        }

        recipe = parse_jsonld_recipe(html_with_jsonld(payload))

        assert recipe.prep_time is None
        assert recipe.cook_time is None
        assert recipe.total_time is None
