"""Test counter reset detection - CRITICAL requirement."""
from app.services.normalization_service import compute_delta


def test_negative_delta_flagged_as_counter_reset():
    """
    CRITICAL: Negative deltas must be flagged as counter resets.
    
    Per requirements: "Negative deltas should be detected as counter resets
    and flagged rather than silently corrected."
    """
    result = compute_delta(current_value=50.0, previous_value=1000.0)
    
    assert "counter_reset" in result["flags"]
    assert result["delta"] is None  # Cannot compute meaningful consumption


def test_first_reading_has_null_delta():
    """First reading should have null delta and 'first_reading' flag."""
    result = compute_delta(current_value=100.0, previous_value=None)
    
    assert "first_reading" in result["flags"]
    assert result["delta"] is None


def test_normal_positive_delta():
    """Normal case: positive delta computed correctly, no flags."""
    result = compute_delta(current_value=150.0, previous_value=100.0)
    
    assert result["delta"] == 50.0
    assert result["flags"] == []


def test_zero_delta():
    """Zero delta (no consumption) should work normally."""
    result = compute_delta(current_value=100.0, previous_value=100.0)
    
    assert result["delta"] == 0.0
    assert result["flags"] == []


def test_suspicious_jump_flagged():
    """Very large deltas should be flagged but still computed."""
    # Default threshold is 10,000 kWh
    result = compute_delta(current_value=15000.0, previous_value=100.0)
    
    assert "suspicious_jump" in result["flags"]
    assert result["delta"] == 14900.0  # Still computed, just flagged