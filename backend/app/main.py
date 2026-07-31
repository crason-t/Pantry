from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, ingredient_customizations, recipes
from app.config import settings

app = FastAPI(title="Pantry API")

# The frontend is served from a different origin than the API (its own port
# per environment), so each allowed origin has to be listed -- see
# Settings.cors_origins for how a given environment sets this.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(recipes.router)
app.include_router(ingredient_customizations.router)
