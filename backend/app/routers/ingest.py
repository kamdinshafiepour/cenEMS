"""Ingestion endpoint - POST /ingest."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging

from app.database import get_db
from app.schemas.ingest import IngestEventRequest, IngestEventResponse
from app.models.raw_event import RawEvent
from app.models.building import Building
from app.models.device import Device
from app.services.deduplication_service import generate_event_id
from app.services.normalization_service import normalize_event
from app.utils.timestamp_utils import normalize_timestamp

# Create router
router = APIRouter()

# Logger
logger = logging.getLogger(__name__)


@router.post(
    "/ingest",
    response_model=IngestEventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Ingest telemetry event",
    description="Accept device telemetry with deduplication and normalization"
)
async def ingest_event(
    event: IngestEventRequest,
    db: Session = Depends(get_db)
) -> IngestEventResponse:
    """
    Ingest a telemetry event.
    
    **Features**:
    - Automatic deduplication (idempotent)
    - Unit normalization (Wh/MWh → kWh)
    - Counter reset detection
    - Out-of-order event handling
    - Quality flag assignment
    
    **Returns**:
    - 201: Event ingested successfully
    - 200: Duplicate event (safe to ignore)
    - 400: Invalid event data
    - 500: Server error
    """
    try:
        # Generate event ID if not provided
        event_id = event.event_id or generate_event_id(event.model_dump())

        # Normalize timestamp for storage
        normalized_ts = normalize_timestamp(event.timestamp)

        # Auto-create Building if it doesn't exist
        building = db.query(Building).filter(Building.building_id == event.building_id).first()
        if not building:
            building = Building(
                building_id=event.building_id,
                name=event.building_id  # Use ID as name initially
            )
            db.add(building)
            db.flush()

        # Auto-create Device if it doesn't exist
        device = db.query(Device).filter(Device.device_id == event.device_id).first()
        if not device:
            device = Device(
                device_id=event.device_id,
                building_id=event.building_id,
                name=event.device_id  # Use ID as name initially
            )
            db.add(device)
            db.flush()

        # Create raw event (immutable audit log)
        raw_event = RawEvent(
            event_id=event_id,
            device_id=event.device_id,
            building_id=event.building_id,
            timestamp=normalized_ts,
            metric_type=event.metric_type,
            value=event.value,
            unit=event.unit,
            raw_payload=event.model_dump()  # Store complete original payload
        )
        
        # Attempt to insert
        db.add(raw_event)
        db.flush()  # Get ID without committing yet
        
        # Normalize event (unit conversion, delta computation, quality flags)
        normalized = normalize_event(db, raw_event)
        
        # Commit transaction
        db.commit()
        
        logger.info(
            "Event ingested",
            extra={
                "event_id": event_id,
                "device_id": event.device_id,
                "metric_type": event.metric_type,
                "quality_flags": normalized.quality_flags
            }
        )
        
        return IngestEventResponse(
            status="ingested",
            event_id=event_id,
            raw_event_id=raw_event.id,
            normalized_measurement_id=normalized.id
        )
        
    except IntegrityError as e:
        # Rollback transaction
        db.rollback()
        
        # Check if duplicate (event_id constraint violation OR device+metric+timestamp)
        if "event_id" in str(e.orig) or "uq_device_metric_timestamp" in str(e.orig):
            logger.info(
                "Duplicate event ignored",
                extra={"event_id": event_id}
            )
            
            # Return 200 OK for duplicates (idempotent behavior)
            return IngestEventResponse(
                status="duplicate",
                event_id=event_id,
                raw_event_id=None,
                normalized_measurement_id=None
            )
        
        # Other integrity errors
        logger.error(f"Database integrity error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data integrity error"
        )

        
    except ValueError as e:
        # Validation errors (invalid timestamp, unsupported unit, etc.)
        db.rollback()
        logger.warning(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
        
    except Exception as e:
        # Unexpected errors
        db.rollback()
        logger.error(f"Unexpected error during ingestion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )
