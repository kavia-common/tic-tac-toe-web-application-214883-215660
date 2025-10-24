from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db import Base, engine
from .routes import router as game_router

app = FastAPI(
    title="Tic Tac Toe API",
    description="REST API for a Tic Tac Toe game with game state tracking and winner detection.",
    version="0.1.0",
    openapi_tags=[
        {"name": "tic-tac-toe", "description": "Game and player endpoints for Tic Tac Toe"},
    ],
)

# Ensure tables exist (simple migration approach for this exercise)
Base.metadata.create_all(bind=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to the Angular app origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check
@app.get("/", tags=["tic-tac-toe"], summary="Health check")
def health_check():
    """Basic health check endpoint returning a simple JSON."""
    return {"message": "Healthy"}

# Include game routes
app.include_router(game_router)
