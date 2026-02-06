"""Timestamp normalization utilities."""
from datetime import datetime
from typing import Union
import pytz


def normalize_timestamp(timestamp: Union[str, datetime]) -> datetime:
    """
    Convert any timezone-aware timestamp to UTC.
    
    Handles:
    - ISO 8601 strings with timezone (e.g., "2026-01-01T10:00:00+05:00")
    - ISO 8601 strings with 'Z' suffix (e.g., "2026-01-01T10:00:00Z")
    - datetime objects (converts to UTC if timezone-aware)
    
    Args:
        timestamp: Timestamp string or datetime object
        
    Returns:
        Timezone-aware datetime in UTC
        
    Raises:
        ValueError: If timestamp format is invalid or naive (no timezone)
        
    Examples:
        >>> normalize_timestamp("2026-01-01T10:00:00+05:00")
        datetime.datetime(2026, 1, 1, 5, 0, 0, tzinfo=<UTC>)
        
        >>> normalize_timestamp("2026-01-01T10:00:00Z")
        datetime.datetime(2026, 1, 1, 10, 0, 0, tzinfo=<UTC>)
    """
    if isinstance(timestamp, str):
        # Replace 'Z' with '+00:00' for consistency
        timestamp = timestamp.replace('Z', '+00:00')
        
        try:
            # Parse ISO 8601 format with timezone
            dt = datetime.fromisoformat(timestamp)
        except ValueError as e:
            raise ValueError(
                f"Invalid timestamp format: {timestamp}. "
                f"Expected ISO 8601 with timezone (e.g., '2026-01-01T10:00:00Z')"
            ) from e
    else:
        dt = timestamp
    
    # Ensure datetime is timezone-aware
    if dt.tzinfo is None:
        raise ValueError(
            f"Timestamp must be timezone-aware. Received naive datetime: {dt}. "
            f"Add timezone info (e.g., append 'Z' for UTC or '+00:00')"
        )
    
    # Convert to UTC
    return dt.astimezone(pytz.UTC)


def is_out_of_order(current_timestamp: datetime, latest_timestamp: datetime) -> bool:
    """
    Check if current timestamp is earlier than the latest processed timestamp.
    
    Args:
        current_timestamp: Timestamp of current event (UTC)
        latest_timestamp: Most recent timestamp already processed (UTC)
        
    Returns:
        True if current event is out of order (arrived late)
        
    Example:
        >>> from datetime import datetime, timezone
        >>> current = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
        >>> latest = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
        >>> is_out_of_order(current, latest)
        True
    """
    return current_timestamp < latest_timestamp
