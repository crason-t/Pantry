from pydantic import BaseModel


class SubstitutionSuggestion(BaseModel):
    """One substitute suggestion for a single ingredient, as Claude produces
    it -- not persisted, see docs/MVP.md ("Substitutions ... are still not
    persisted for MVP; computed on demand via Claude each time")."""

    substitute: str
    reason: str


class SubstitutionSuggestions(BaseModel):
    """Response shape for the substitutions endpoint. Doubles as the
    structured-output schema for the Claude call itself -- there's no
    resolution step against DB rows the way insight generation has, so one
    model covers both the Claude call and the API response."""

    suggestions: list[SubstitutionSuggestion]
