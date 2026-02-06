"""
Normalization service - core business logic for telemetry processing.

Handles:
- Counter reset detection (negative deltas)
- Out-of-order event processing
- Delta computation for energy consumption
- Quality flag assignment
"""
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy.orm import Session

from app.models.raw_event import RawEvent
from app.models.normalized_measurement import NormalizedMeasurement
from app.utils.unit_converter import normalize_unit, get_standard_unit
from app.utils.timestamp_utils import normalize_timestamp
from app.config import settings


def compute_delta(
    current_value: float,
    previous_value: Optional[float],
    metric_type: str = "energy"
) -> Dict[str, any]:
    """
    Compute delta (consumption) with counter reset detection.
    
    **CRITICAL REQUIREMENT**: Per spec, negative deltas must be flagged,
    NOT corrected. We return None for delta when counter reset is detected.
    
    Args:
        current_value: Current cumulative reading
        previous_value: Previous cumulative reading (None for first reading)
        metric_type: Type of metric for context
        
    Returns:
        Dict with:
        - "delta": float or None (None for resets/first reading)
        - "flags": list of quality flag strings
        
    Quality flags:
        - "first_reading": No previous value to compare
        - "counter_reset": Negative delta detected (likely meter reset)
        - "suspicious_jump": Unusually large positive delta
        
    Examples:
        >>> compute_delta(150, 100)
        {"delta": 50.0, "flags": []}
        
        >>> compute_delta(50, 1000)  # Counter reset
        {"delta": None, "flags": ["counter_reset"]}
        
        >>> compute_delta(100, None)  # First reading
        {"delta": None, "flags": ["first_reading"]}
    """
    flags = []
    
    # First reading - no previous value to compare
    if previous_value is None:
        return {
            "delta": None,
            "flags": ["first_reading"]
        }

    # Compute delta (convert to float to handle Decimal from database)
    delta = float(current_value) - float(previous_value)
    
    # NEGATIVE DELTA = COUNTER RESET
    # Per requirements: "Negative deltas should be detected as counter resets
    # and flagged rather than silently corrected"
    if delta < 0:
        return {
            "delta": None,  # Cannot compute meaningful consumption
            "flags": ["counter_reset"]
        }
    
    # Detect suspiciously large jumps (possible data error)
    # Threshold from settings (default 10,000 kWh)
    if delta > settings.max_reasonable_delta:
        flags.append("suspicious_jump")
    
    return {
        "delta": delta,
        "flags": flags
    }


def get_previous_measurement(
    db: Session,
    device_id: str,
    metric_type: str,
    before_timestamp: Optional[datetime] = None
) -> Optional[NormalizedMeasurement]:
    """
    Get the most recent measurement before a given timestamp.
    
    Used for:
    - Computing deltas
    - Detecting out-of-order events
    
    Args:
        db: Database session
        device_id: Device identifier
        metric_type: Metric type (e.g., "energy")
        before_timestamp: Get measurement before this time (None = most recent)
        
    Returns:
        Most recent measurement or None if no previous measurement exists
    """
    query = db.query(NormalizedMeasurement).filter(
        NormalizedMeasurement.device_id == device_id,
        NormalizedMeasurement.metric_type == metric_type
    )
    
    if before_timestamp:
        query = query.filter(NormalizedMeasurement.timestamp < before_timestamp)
    
    return query.order_by(NormalizedMeasurement.timestamp.desc()).first()


def get_next_measurement(
    db: Session,
    device_id: str,
    metric_type: str,
    after_timestamp: datetime
) -> Optional[NormalizedMeasurement]:
    """
    Get the next measurement after a given timestamp.
    
    Used for recomputing deltas when out-of-order events arrive.
    
    Args:
        db: Database session
        device_id: Device identifier
        metric_type: Metric type
        after_timestamp: Get measurement after this time
        
    Returns:
        Next measurement or None if this is the latest
    """
    return db.query(NormalizedMeasurement).filter(
        NormalizedMeasurement.device_id == device_id,
        NormalizedMeasurement.metric_type == metric_type,
        NormalizedMeasurement.timestamp > after_timestamp
    ).order_by(NormalizedMeasurement.timestamp.asc()).first()


def recompute_delta(
    db: Session,
    measurement: NormalizedMeasurement
) -> None:
    """
    Recompute delta for a measurement (used after out-of-order insertions).
    
    When an out-of-order event arrives, it affects the delta of the next
    measurement. This function recalculates and updates it.
    
    Args:
        db: Database session
        measurement: Measurement to recompute
    """
    # Get the previous measurement (now potentially different)
    prev = get_previous_measurement(
        db,
        measurement.device_id,
        measurement.metric_type,
        before_timestamp=measurement.timestamp
    )
    
    # Recompute delta
    delta_result = compute_delta(
        measurement.value,
        prev.value if prev else None,
        measurement.metric_type
    )
    
    # Update measurement
    measurement.delta_value = delta_result["delta"]
    
    # Merge quality flags (keep existing flags, add new ones)
    existing_flags = set(measurement.quality_flags or [])
    new_flags = set(delta_result["flags"])
    measurement.quality_flags = list(existing_flags | new_flags)
    
    db.commit()


def normalize_event(
    db: Session,
    raw_event: RawEvent
) -> NormalizedMeasurement:
    """
    Normalize a raw event into a queryable measurement.
    
    This is the MAIN ORCHESTRATION FUNCTION that:
    1. Normalizes units and timestamps
    2. Detects out-of-order events
    3. Computes deltas with counter reset detection
    4. Recomputes affected measurements
    5. Assigns quality flags
    
    Args:
        db: Database session
        raw_event: Raw event to normalize
        
    Returns:
        Created NormalizedMeasurement
    """
    quality_flags: List[str] = []
    
    # Normalize timestamp to UTC
    normalized_timestamp = normalize_timestamp(raw_event.timestamp)
    
    # Get most recent measurement for this device/metric
    latest_measurement = get_previous_measurement(
        db,
        raw_event.device_id,
        raw_event.metric_type
    )
    
    # CHECK FOR OUT-OF-ORDER EVENT
    is_out_of_order = False
    if latest_measurement and normalized_timestamp < latest_measurement.timestamp:
        quality_flags.append("out_of_order")
        is_out_of_order = True
    
    # Get correct previous measurement (considering out-of-order)
    prev_measurement = get_previous_measurement(
        db,
        raw_event.device_id,
        raw_event.metric_type,
        before_timestamp=normalized_timestamp
    )
    
    # Normalize unit (e.g., Wh → kWh)
    normalized_value = normalize_unit(
        raw_event.value,
        raw_event.unit,
        raw_event.metric_type
    )
    
    # Compute delta with counter reset detection
    delta_result = compute_delta(
        normalized_value,
        prev_measurement.value if prev_measurement else None,
        raw_event.metric_type
    )
    
    # Merge quality flags
    quality_flags.extend(delta_result["flags"])
    
    # Create normalized measurement
    normalized = NormalizedMeasurement(
        raw_event_id=raw_event.id,
        device_id=raw_event.device_id,
        building_id=raw_event.building_id,
        timestamp=normalized_timestamp,
        metric_type=raw_event.metric_type,
        value=normalized_value,
        unit=get_standard_unit(raw_event.metric_type),
        delta_value=delta_result["delta"],
        quality_flags=quality_flags
    )
    
    db.add(normalized)
    db.flush()  # Get ID without committing
    
    # If out-of-order, recompute delta for next measurement
    if is_out_of_order:
        next_measurement = get_next_measurement(
            db,
            raw_event.device_id,
            raw_event.metric_type,
            after_timestamp=normalized_timestamp
        )
        
        if next_measurement:
            recompute_delta(db, next_measurement)
    
    return normalized
