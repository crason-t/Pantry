from fastapi import FastAPI

from app.api.routes import auth, health

app = FastAPI(title="Pantry API")

app.include_router(health.router)
app.include_router(auth.router)
