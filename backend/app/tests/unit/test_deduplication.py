"""Test deduplication service."""
from app.services.deduplication_service import generate_event_id


def test_identical_payloads_generate_same_event_id():
    """Identical events should produce identical event IDs."""
    payload1 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T10:00:00Z",
        "metric_type": "energy",
        "value": 100.0
    }
    payload2 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T10:00:00Z",
        "metric_type": "energy",
        "value": 100.0
    }
    
    event_id1 = generate_event_id(payload1)
    event_id2 = generate_event_id(payload2)
    
    assert event_id1 == event_id2
    assert len(event_id1) == 64  # SHA256 produces 64 hex characters


def test_different_values_generate_different_ids():
    """Different values should produce different event IDs."""
    payload1 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T10:00:00Z",
        "metric_type": "energy",
        "value": 100.0
    }
    payload2 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T10:00:00Z",
        "metric_type": "energy",
        "value": 101.0  # Different value
    }
    
    event_id1 = generate_event_id(payload1)
    event_id2 = generate_event_id(payload2)
    
    assert event_id1 != event_id2


def test_different_timestamps_generate_different_ids():
    """Different timestamps should produce different event IDs."""
    payload1 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T10:00:00Z",
        "metric_type": "energy",
        "value": 100.0
    }
    payload2 = {
        "device_id": "meter-001",
        "timestamp": "2026-01-01T11:00:00Z",  # Different timestamp
        "metric_type": "energy",
        "value": 100.0
    }
    
    event_id1 = generate_event_id(payload1)
    event_id2 = generate_event_id(payload2)
    
    assert event_id1 != event_id2
