"""Query endpoints - GET /latest, /timeseries, /buildings, /devices."""
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.schemas.query import (
    LatestReadingResponse,
    TimeSeriesResponse,
    MeasurementData,
    BuildingsResponse,
    BuildingInfo,
    DevicesResponse,
    DeviceInfo
)
from app.models.normalized_measurement import NormalizedMeasurement
from app.models.device import Device
from app.models.building import Building

# Create router
router = APIRouter()


@router.get(
    "/latest",
    response_model=LatestReadingResponse,
    summary="Get latest reading",
    description="Get the most recent measurement for a device"
)
async def get_latest(
    device_id: str = Query(..., description="Device identifier"),
    metric_type: str = Query(..., description="Metric type (e.g., 'energy')"),
    db: Session = Depends(get_db)
) -> LatestReadingResponse:
    """Get latest measurement for a device."""
    
    # Query latest measurement
    measurement = db.query(NormalizedMeasurement).filter(
        NormalizedMeasurement.device_id == device_id,
        NormalizedMeasurement.metric_type == metric_type
    ).order_by(NormalizedMeasurement.timestamp.desc()).first()
    
    if not measurement:
        # No data yet - return empty response
        return LatestReadingResponse(
            device_id=device_id,
            building_id="unknown",
            metric_type=metric_type,
            latest_reading=None
        )
    
    return LatestReadingResponse(
        device_id=device_id,
        building_id=measurement.building_id,
        metric_type=metric_type,
        latest_reading=MeasurementData.model_validate(measurement)
    )


@router.get(
    "/timeseries",
    response_model=TimeSeriesResponse,
    summary="Get time-series data",
    description="Get measurements for a device within a time range"
)
async def get_timeseries(
    device_id: str = Query(..., description="Device identifier"),
    metric_type: str = Query(..., description="Metric type"),
    start: datetime = Query(..., description="Start time (ISO 8601)"),
    end: datetime = Query(..., description="End time (ISO 8601)"),
    db: Session = Depends(get_db)
) -> TimeSeriesResponse:
    """Get time-series measurements for a device."""
    
    # Validate time range
    if start >= end:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    
    # Query measurements in time range
    measurements = db.query(NormalizedMeasurement).filter(
        NormalizedMeasurement.device_id == device_id,
        NormalizedMeasurement.metric_type == metric_type,
        NormalizedMeasurement.timestamp >= start,
        NormalizedMeasurement.timestamp <= end
    ).order_by(NormalizedMeasurement.timestamp.asc()).all()
    
    return TimeSeriesResponse(
        device_id=device_id,
        metric_type=metric_type,
        measurements=[MeasurementData.model_validate(m) for m in measurements]
    )


@router.get(
    "/buildings",
    response_model=BuildingsResponse,
    summary="List buildings",
    description="Get all buildings with device counts"
)
async def get_buildings(
    db: Session = Depends(get_db)
) -> BuildingsResponse:
    """List all buildings with device counts."""
    
    # Query buildings with device counts
    buildings = db.query(
        Building,
        func.count(Device.device_id).label('device_count')
    ).outerjoin(
        Device, Building.building_id == Device.building_id
    ).group_by(Building.building_id).all()
    
    return BuildingsResponse(
        buildings=[
            BuildingInfo(
                building_id=building.building_id,
                name=building.name,
                address=building.address,
                device_count=device_count
            )
            for building, device_count in buildings
        ]
    )


@router.get(
    "/devices",
    response_model=DevicesResponse,
    summary="List devices",
    description="Get all devices, optionally filtered by building"
)
async def get_devices(
    building_id: Optional[str] = Query(None, description="Filter by building ID"),
    db: Session = Depends(get_db)
) -> DevicesResponse:
    """List devices, optionally filtered by building."""
    
    # Query devices
    query = db.query(Device)
    
    if building_id:
        query = query.filter(Device.building_id == building_id)
    
    devices = query.all()
    
    return DevicesResponse(
        devices=[DeviceInfo.model_validate(d) for d in devices]
    )
