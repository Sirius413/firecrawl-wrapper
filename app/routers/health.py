from fastapi import APIRouter

from app.schemas import HealthResponse


router = APIRouter()

@router.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
