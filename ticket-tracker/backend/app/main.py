from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import epics, health, tickets

app = FastAPI(title="Pantry Ticket Tracker")

# Local dev only: frontend runs on Vite's default port for this app, a
# different origin than the API. Revisit once there's a deployment target.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5180"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(epics.router)
app.include_router(tickets.router)
