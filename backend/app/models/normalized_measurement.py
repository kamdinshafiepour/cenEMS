"""NormalizedMeasurement model - processed and queryable time-series data."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey, Index, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from app.database import Base


class NormalizedMeasurement(Base):
    """Normalized and processed measurements with quality indicators."""
    
    __tablename__ = "normalized_measurements"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to raw event (audit trail)
    raw_event_id = Column(Integer, ForeignKey('raw_events.id'), nullable=False)
    
    # Event metadata
    device_id = Column(String(100), nullable=False)
    building_id = Column(String(100), nullable=False)
    
    # Normalized timestamp (always UTC)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    
    # Measurement data (normalized)
    metric_type = Column(String(50), nullable=False)
    value = Column(Numeric(15, 6), nullable=False)  # Normalized value
    unit = Column(String(20), nullable=False)  # Standardized unit (kWh, kW, etc.)
    
    # Derived metrics
    delta_value = Column(Numeric(15, 6), nullable=True)  # NULL for counter resets or first reading
    
    # Quality indicators
    quality_flags = Column(ARRAY(String), nullable=False, default=list, server_default='{}')
    # Possible flags: 'first_reading', 'counter_reset', 'out_of_order', 'suspicious_jump'
    
    # Creation timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'))
    
    # Indexes and constraints
    __table_args__ = (
        # Prevent duplicate normalized entries
        UniqueConstraint('device_id', 'metric_type', 'timestamp', name='uq_device_metric_timestamp'),
        # Query optimization indexes
        Index('idx_normalized_device_metric_time', 'device_id', 'metric_type', 'timestamp'),
        Index('idx_normalized_building_time', 'building_id', 'timestamp'),
        Index('idx_normalized_quality_flags', 'quality_flags', postgresql_using='gin'),
    )
