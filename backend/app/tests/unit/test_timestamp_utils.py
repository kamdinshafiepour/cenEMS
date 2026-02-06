"""Test timestamp normalization utilities."""
import pytest
from datetime import datetime, timezone
from app.utils.timestamp_utils import normalize_timestamp, is_out_of_order


def test_timezone_conversion_to_utc():
    """Non-UTC timestamps should convert to UTC."""
    # +05:00 timezone
    input_ts = "2026-01-01T10:00:00+05:00"
    normalized = normalize_timestamp(input_ts)
    
    # Should be 5 hours earlier in UTC
    assert normalized.hour == 5
    assert normalized.tzinfo.tzname(None) == "UTC"


def test_utc_timestamp_unchanged():
    """Already UTC timestamps should remain unchanged."""
    input_ts = "2026-01-01T10:00:00Z"
    normalized = normalize_timestamp(input_ts)
    
    assert normalized.year == 2026
    assert normalized.month == 1
    assert normalized.day == 1
    assert normalized.hour == 10
    assert normalized.tzinfo.tzname(None) == "UTC"


def test_plus_zero_timezone():
    """Timestamps with +00:00 should be UTC."""
    input_ts = "2026-01-01T10:00:00+00:00"
    normalized = normalize_timestamp(input_ts)
    
    assert normalized.hour == 10
    assert normalized.tzinfo.tzname(None) == "UTC"


def test_negative_timezone_offset():
    """Negative timezone offsets should work correctly."""
    # -08:00 (Pacific Time)
    input_ts = "2026-01-01T10:00:00-08:00"
    normalized = normalize_timestamp(input_ts)
    
    # Should be 8 hours later in UTC
    assert normalized.hour == 18
    assert normalized.tzinfo.tzname(None) == "UTC"


def test_invalid_timestamp_raises_error():
    """Invalid timestamp strings should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        normalize_timestamp("not-a-timestamp")
    
    with pytest.raises(ValueError, match="Invalid timestamp format"):
        normalize_timestamp("2026-13-01T10:00:00Z")  # Invalid month


def test_naive_datetime_raises_error():
    """Naive datetime (no timezone) should raise ValueError."""
    naive_dt = datetime(2026, 1, 1, 10, 0, 0)  # No tzinfo
    
    with pytest.raises(ValueError, match="must be timezone-aware"):
        normalize_timestamp(naive_dt)


def test_is_out_of_order():
    """Should correctly detect out-of-order timestamps."""
    current = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    latest = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    
    # current < latest → out of order
    assert is_out_of_order(current, latest) is True


def test_is_not_out_of_order():
    """Should correctly detect in-order timestamps."""
    current = datetime(2026, 1, 1, 13, 0, tzinfo=timezone.utc)
    latest = datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc)
    
    # current > latest → in order
    assert is_out_of_order(current, latest) is False
