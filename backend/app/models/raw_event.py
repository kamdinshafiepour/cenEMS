"""RawEvent model - immutable audit log of all incoming telemetry."""
from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index, text
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime
from app.database import Base


class RawEvent(Base):
    """Raw telemetry events as received (immutable audit log)."""
    
    __tablename__ = "raw_events"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Deduplication key (SHA256 hash)
    event_id = Column(String(64), nullable=False, unique=True, index=True)
    
    # Event metadata
    device_id = Column(String(100), nullable=False)
    building_id = Column(String(100), nullable=False)
    
    # Timestamps
    timestamp = Column(DateTime(timezone=True), nullable=False)  # Original event time
    received_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'))  # Server receive time
    
    # Measurement data
    metric_type = Column(String(50), nullable=False)  # 'energy', 'power', etc.
    value = Column(Numeric(15, 6), nullable=False)
    unit = Column(String(20), nullable=False)  # Original unit as received
    
    # Full original payload for audit trail
    raw_payload = Column(JSONB, nullable=False)
    
    # Creation timestamp
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'))
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_raw_events_device_timestamp', 'device_id', 'timestamp'),
        Index('idx_raw_events_received_at', 'received_at'),
    )
