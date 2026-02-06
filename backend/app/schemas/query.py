"""Schemas for query endpoints."""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class MeasurementData(BaseModel):
    """Schema for a single measurement."""
    
    timestamp: datetime = Field(..., description="Measurement timestamp (UTC)")
    value: float = Field(..., description="Normalized value")
    unit: str = Field(..., description="Standard unit (e.g., 'kWh')")
    delta_value: Optional[float] = Field(None, description="Consumption delta (null for resets/first reading)")
    quality_flags: List[str] = Field(default=[], description="Quality indicators")
    
    class Config:
        from_attributes = True  # Allow creation from SQLAlchemy models


class LatestReadingResponse(BaseModel):
    """Response for GET /latest."""
    
    device_id: str
    building_id: str
    metric_type: str
    latest_reading: Optional[MeasurementData] = Field(
        None,
        description="Most recent measurement (null if no data)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "meter-001",
                "building_id": "building-a",
                "metric_type": "energy",
                "latest_reading": {
                    "timestamp": "2026-01-01T10:00:00Z",
                    "value": 1234.56,
                    "unit": "kWh",
                    "delta_value": 12.3,
                    "quality_flags": []
                }
            }
        }


class TimeSeriesResponse(BaseModel):
    """Response for GET /timeseries."""
    
    device_id: str
    metric_type: str
    measurements: List[MeasurementData] = Field(
        default=[],
        description="List of measurements in time range"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "meter-001",
                "metric_type": "energy",
                "measurements": [
                    {
                        "timestamp": "2026-01-01T10:00:00Z",
                        "value": 1100.0,
                        "unit": "kWh",
                        "delta_value": 10.5,
                        "quality_flags": []
                    },
                    {
                        "timestamp": "2026-01-01T11:00:00Z",
                        "value": 50.0,
                        "unit": "kWh",
                        "delta_value": None,
                        "quality_flags": ["counter_reset"]
                    }
                ]
            }
        }


class DeviceInfo(BaseModel):
    """Schema for device metadata."""
    
    device_id: str
    building_id: str
    name: Optional[str] = None
    location: Optional[str] = None
    device_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class DevicesResponse(BaseModel):
    """Response for GET /devices."""
    
    devices: List[DeviceInfo] = Field(default=[], description="List of devices")


class BuildingInfo(BaseModel):
    """Schema for building metadata."""
    
    building_id: str
    name: str
    address: Optional[str] = None
    device_count: int = Field(0, description="Number of devices in building")


class BuildingsResponse(BaseModel):
    """Response for GET /buildings."""
    
    buildings: List[BuildingInfo] = Field(default=[], description="List of buildings")


class HealthResponse(BaseModel):
    """Response for GET /health."""
    
    status: str = Field(..., description="Service status: 'ok' or 'error'")
    timestamp: datetime = Field(..., description="Current server time")
    database: str = Field(..., description="Database status: 'connected' or 'disconnected'")
    version: str = Field(..., description="API version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ok",
                "timestamp": "2026-01-01T10:00:00Z",
                "database": "connected",
                "version": "1.0.0"
            }
        }
