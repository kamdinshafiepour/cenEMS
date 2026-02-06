"""Deduplication service - generates deterministic event IDs."""
import hashlib
from typing import Dict, Any


def generate_event_id(payload: Dict[str, Any]) -> str:
    """
    Generate deterministic SHA256 event ID from payload.
    
    Same payload always produces same ID (idempotent deduplication).
    
    Args:
        payload: Event data containing device_id, timestamp, metric_type, value
        
    Returns:
        64-character hex string (SHA256 hash)
        
    Example:
        >>> payload = {
        ...     "device_id": "meter-001",
        ...     "timestamp": "2026-01-01T10:00:00Z",
        ...     "metric_type": "energy",
        ...     "value": 1234.56
        ... }
        >>> event_id = generate_event_id(payload)
        >>> len(event_id)
        64
    """
    # Create canonical string representation
    # Order matters for consistency!
    canonical = (
        f"{payload.get('device_id', '')}|"
        f"{payload.get('timestamp', '')}|"
        f"{payload.get('metric_type', '')}|"
        f"{payload.get('value', '')}"
    )
    
    # Generate SHA256 hash
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()
