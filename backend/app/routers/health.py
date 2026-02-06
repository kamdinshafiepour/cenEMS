"""Health check endpoint - GET /health."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

from app.database import get_db
from app.schemas.query import HealthResponse
from app.config import settings

# Create router
router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Health check",
    description="Check service and database connectivity"
)
async def health_check(
    db: Session = Depends(get_db)
) -> HealthResponse:
    """
    Health check endpoint.
    
    Returns service status and database connectivity.
    Used by monitoring systems and load balancers.
    """
    
    # Test database connection
    try:
        # Execute simple query to verify database is responsive
        db.execute(text("SELECT 1"))
        database_status = "connected"
        service_status = "ok"
    except Exception as e:
        database_status = "disconnected"
        service_status = "degraded"
    
    return HealthResponse(
        status=service_status,
        timestamp=datetime.utcnow(),
        database=database_status,
        version=settings.app_version
    )
