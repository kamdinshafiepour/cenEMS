"""Schemas for telemetry ingestion endpoints."""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class IngestEventRequest(BaseModel):
    """Request schema for POST /ingest."""
    
    event_id: Optional[str] = Field(
        None,
        description="Optional client-provided event ID for deduplication"
    )
    device_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Unique device identifier"
    )
    building_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Building identifier where device is located"
    )
    timestamp: str = Field(
        ...,
        description="Event timestamp in ISO 8601 format with timezone (e.g., '2026-01-01T10:00:00Z')"
    )
    metric_type: str = Field(
        ...,
        description="Type of metric (e.g., 'energy', 'power', 'temperature')"
    )
    value: float = Field(
        ...,
        description="Measurement value"
    )
    unit: str = Field(
        ...,
        description="Unit of measurement (e.g., 'kWh', 'Wh', 'MWh', 'kW')"
    )
    
    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v: str) -> str:
        """Ensure timestamp is valid ISO 8601 format."""
        try:
            # Try parsing to validate format
            if 'Z' in v or '+' in v or v.endswith('00:00'):
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            else:
                raise ValueError("Timestamp must include timezone (e.g., 'Z' or '+00:00')")
        except Exception as e:
            raise ValueError(f"Invalid timestamp format: {e}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "meter-001",
                "building_id": "building-a",
                "timestamp": "2026-01-01T10:00:00Z",
                "metric_type": "energy",
                "value": 1234.56,
                "unit": "kWh"
            }
        }


class IngestEventResponse(BaseModel):
    """Response schema for POST /ingest."""
    
    status: str = Field(
        ...,
        description="Status: 'ingested' for new events, 'duplicate' for duplicates"
    )
    event_id: str = Field(
        ...,
        description="Event ID (generated or provided)"
    )
    raw_event_id: Optional[int] = Field(
        None,
        description="Database ID of raw event (null for duplicates)"
    )
    normalized_measurement_id: Optional[int] = Field(
        None,
        description="Database ID of normalized measurement (null for duplicates)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "ingested",
                "event_id": "a1b2c3d4...",
                "raw_event_id": 123,
                "normalized_measurement_id": 456
            }
        }
