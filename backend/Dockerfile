# Pantry API image.
#
# Not used by local environments (scripts/pantry-env runs uvicorn directly so
# reloads stay instant). This exists so a hosted environment is a deploy of
# config rather than a rewrite: every setting the app needs already comes from
# environment variables -- see backend/app/config.py.

FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencies resolve from the lockfile in their own layer, so application
# edits don't invalidate the (slow) dependency install.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app

RUN uv sync --frozen --no-dev

ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000

# Migrations are deliberately not run here -- a container that migrates on
# boot races itself when more than one replica starts. Run `alembic upgrade
# head` as a release step instead.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
