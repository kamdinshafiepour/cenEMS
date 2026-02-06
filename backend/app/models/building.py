"""Building model - metadata about buildings containing devices."""
from sqlalchemy import Column, String, Text, DateTime, text
from app.database import Base


class Building(Base):
    """Building metadata."""
    
    __tablename__ = "buildings"

    # Primary key
    building_id = Column(String(100), primary_key=True)
    
    # Building information
    name = Column(String(200), nullable=False)
    address = Column(Text, nullable=True)  # Text type for longer addresses
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=text('NOW()'))
