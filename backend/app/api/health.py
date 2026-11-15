"""Health check endpoint."""

from fastapi import APIRouter
from sqlalchemy import text
from app.db import engine

router = APIRouter()


@router.get("/health", tags=["health"], summary="Check API health")
def health_check() -> dict[str, str]:
    """Return a simple liveness response."""
    return {"status": "ok"}

@router.get("/health/db")
def health_db():
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    return {"database": "ok"}