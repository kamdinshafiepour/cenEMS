"""Device model - metadata about energy monitoring devices."""
from sqlalchemy import Column, String, DateTime, text
from app.database import Base


class Device(Base):
    """Energy monitoring device metadata."""
    
    __tablename__ = "devices"

    # Primary key
    device_id = Column(String(100), primary_key=True)
    
    # Device belongs to a building
    building_id = Column(String(100), nullable=False)
    
    # Device information
    name = Column(String(200), nullable=True)
    location = Column(String(200), nullable=True)  # e.g., "Electrical Room", "Floor 3"
    device_type = Column(String(50), nullable=True)  # e.g., "smart_meter", "sensor"
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'))
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'), onupdate=text('NOW()'))
