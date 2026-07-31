from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", env_file_encoding="utf-8", extra="ignore")

    database_url: str
    anthropic_api_key: str = ""
    claude_model: str = "claude-opus-5"
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Which named environment this process serves -- "dev" locally, or
    # "silver"/"capsule-1"/... when launched via scripts/pantry-env. Surfaced
    # on /health so it's unambiguous which stack you're talking to.
    environment_name: str = "dev"

    # Browsers block cross-origin API calls, so every frontend origin allowed
    # to call this backend has to be listed. Each environment serves its own
    # frontend on its own port, hence per-environment config rather than a
    # hardcoded list (a hosted deploy sets its real origin here).
    # NoDecode: without it pydantic-settings would try to JSON-parse the env
    # var before the validator below ever sees it.
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        """Accept a comma-separated string -- env vars can't carry lists."""
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


settings = Settings()
