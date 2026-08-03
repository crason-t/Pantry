"""Tests for the ingestion pipeline's routing decision.

Both ingestion paths converge on `ParsedRecipe`, but only one of them costs an
LLM call. The rule (docs/MVP.md): URL ingestion uses JSON-LD when it yields a
*complete* recipe and falls back to Claude otherwise; pasted text always goes
to Claude. These tests pin that decision down -- a regression here is silent,
showing up only as a surprise API bill or a needlessly empty recipe.

The real `parse_jsonld_recipe` runs against real HTML here; only the network
fetch and the Claude call are stubbed.
"""

import json

import pytest

from app.schemas.recipe import ParsedIngredient, ParsedRecipe, ParsedStep
from app.services.ingestion import pipeline
from tests.test_jsonld_parser import COMPLETE_RECIPE, html_with_jsonld

CLAUDE_RESULT = ParsedRecipe(
    title="Extracted By Claude",
    ingredients=[ParsedIngredient(name="rice", raw_text="1 cup rice")],
    steps=[ParsedStep(instruction="Cook the rice.")],
)


class ClaudeSpy:
    """Stands in for `extract_recipe_with_claude`, recording its input."""

    def __init__(self):
        self.calls: list[str] = []

    def __call__(self, text: str) -> ParsedRecipe:
        self.calls.append(text)
        return CLAUDE_RESULT

    @property
    def called(self) -> bool:
        return bool(self.calls)


@pytest.fixture
def claude(monkeypatch) -> ClaudeSpy:
    spy = ClaudeSpy()
    monkeypatch.setattr(pipeline, "extract_recipe_with_claude", spy)
    return spy


@pytest.fixture
def serve_html(monkeypatch):
    """Make `fetch_html` return a fixed page instead of hitting the network."""

    def _serve(html: str):
        monkeypatch.setattr(pipeline, "fetch_html", lambda url: html)

    return _serve


class TestUrlIngestionUsesJsonld:
    def test_complete_jsonld_skips_the_claude_call(self, claude, serve_html):
        serve_html(html_with_jsonld(COMPLETE_RECIPE))

        recipe = pipeline.ingest_from_url("https://example.com/chicken")

        assert not claude.called
        assert recipe.title == "Sheet-Pan Chicken Thighs"
        assert len(recipe.ingredients) == 3
        assert len(recipe.steps) == 3


class TestUrlIngestionFallsBackToClaude:
    def test_falls_back_when_the_page_has_no_jsonld(self, claude, serve_html):
        page = "<html><body><h1>Chicken Thighs</h1><p>Roast them.</p></body></html>"
        serve_html(page)

        recipe = pipeline.ingest_from_url("https://example.com/chicken")

        assert claude.called
        assert recipe == CLAUDE_RESULT

    def test_falls_back_when_jsonld_has_no_ingredients(self, claude, serve_html):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeIngredient"}
        serve_html(html_with_jsonld(payload))

        recipe = pipeline.ingest_from_url("https://example.com/chicken")

        assert claude.called
        assert recipe == CLAUDE_RESULT

    def test_falls_back_when_jsonld_has_no_steps(self, claude, serve_html):
        payload = {k: v for k, v in COMPLETE_RECIPE.items() if k != "recipeInstructions"}
        serve_html(html_with_jsonld(payload))

        recipe = pipeline.ingest_from_url("https://example.com/chicken")

        assert claude.called
        assert recipe == CLAUDE_RESULT

    def test_falls_back_when_jsonld_is_present_but_not_a_recipe(self, claude, serve_html):
        serve_html(html_with_jsonld({"@type": "Article", "name": "Ten Best Chickens"}))

        recipe = pipeline.ingest_from_url("https://example.com/listicle")

        assert claude.called
        assert recipe == CLAUDE_RESULT

    def test_fallback_hands_claude_the_full_page_html(self, claude, serve_html):
        page = "<html><body><h1>Chicken Thighs</h1></body></html>"
        serve_html(page)

        pipeline.ingest_from_url("https://example.com/chicken")

        assert claude.calls == [page]


class TestUrlIsFetchedBeforeParsing:
    def test_passes_the_requested_url_to_the_fetcher(self, claude, monkeypatch):
        fetched: list[str] = []

        def fake_fetch(url: str) -> str:
            fetched.append(url)
            return html_with_jsonld(COMPLETE_RECIPE)

        monkeypatch.setattr(pipeline, "fetch_html", fake_fetch)

        pipeline.ingest_from_url("https://example.com/chicken?utm_source=x")

        assert fetched == ["https://example.com/chicken?utm_source=x"]


class TestTextIngestion:
    def test_always_calls_claude(self, claude):
        recipe = pipeline.ingest_from_text("Chicken thighs. Roast at 425F.")

        assert claude.calls == ["Chicken thighs. Roast at 425F."]
        assert recipe == CLAUDE_RESULT

    def test_does_not_shortcut_on_embedded_jsonld(self, claude):
        """Pasted text has no structured markup to trust, so even text that
        happens to contain JSON-LD still goes through Claude."""
        pasted = json.dumps(COMPLETE_RECIPE)

        recipe = pipeline.ingest_from_text(pasted)

        assert claude.calls == [pasted]
        assert recipe == CLAUDE_RESULT

    def test_never_touches_the_network(self, claude, monkeypatch):
        def explode(url: str) -> str:
            raise AssertionError("text ingestion must not fetch a URL")

        monkeypatch.setattr(pipeline, "fetch_html", explode)

        assert pipeline.ingest_from_text("Chicken thighs.") == CLAUDE_RESULT
