from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, health, recipes

app = FastAPI(title="Pantry API")

# Local dev only: frontend runs on Vite's default port, a different origin
# than the API. Revisit this list once there's an actual deployment target.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(recipes.router)
