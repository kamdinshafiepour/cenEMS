"""
CenEMS Telemetry Service - Main FastAPI Application.

Energy monitoring telemetry ingestion and normalization service.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.utils.logger import setup_logging
from app.routers import ingest, query, health

# Setup logging
setup_logging()

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Energy telemetry ingestion and normalization service.
    
    ## Features
    - **Deduplication**: Idempotent ingestion (duplicates ignored)
    - **Unit Normalization**: Converts Wh/MWh to standard kWh
    - **Counter Reset Detection**: Flags negative deltas (meter resets)
    - **Out-of-Order Handling**: Accepts late events, recomputes deltas
    - **Quality Flags**: Transparent data quality indicators
    
    ## Endpoints
    - POST /ingest - Ingest telemetry events
    - GET /latest - Get latest reading for device
    - GET /timeseries - Get historical data
    - GET /buildings - List buildings
    - GET /devices - List devices
    - GET /health - Health check
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware (allow frontend to call API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ingest.router, tags=["Ingestion"])
app.include_router(query.router, tags=["Query"])
app.include_router(health.router, tags=["Health"])


@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint - redirects to API docs."""
    return {
        "message": "CenEMS Telemetry Service",
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health"
    }
