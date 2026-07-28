from functools import lru_cache

import anthropic

from app.config import settings


@lru_cache(maxsize=1)
def get_claude_client() -> anthropic.Anthropic:
    """One shared Anthropic client for the app.

    If ANTHROPIC_API_KEY is unset, falls through to the SDK's own credential
    resolution (ANTHROPIC_AUTH_TOKEN, an `ant auth login` profile, etc.)
    rather than failing outright.
    """
    if settings.anthropic_api_key:
        return anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return anthropic.Anthropic()


def get_model() -> str:
    return settings.claude_model
