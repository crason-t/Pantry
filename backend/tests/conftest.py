"""Test-suite bootstrap.

`Settings` (app/config.py) has no defaults for `database_url` or
`jwt_secret_key`, so importing anything under `app.` fails outright without
them. Setting throwaway values here -- before any test module imports the app
-- keeps the suite runnable on a clean checkout and in CI with no .env file,
no database, and no Anthropic credentials.
"""

import os

os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://test:test@localhost/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-only-signing-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-only-not-a-real-key")
