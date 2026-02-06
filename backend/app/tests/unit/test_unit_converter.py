"""Test unit conversion utilities."""
import pytest
from app.utils.unit_converter import normalize_unit, get_standard_unit


def test_wh_to_kwh_conversion():
    """Wh should convert to kWh correctly."""
    assert normalize_unit(1000, "Wh", "energy") == 1.0
    assert normalize_unit(500, "Wh", "energy") == 0.5
    assert normalize_unit(2500, "Wh", "energy") == 2.5


def test_mwh_to_kwh_conversion():
    """MWh should convert to kWh correctly."""
    assert normalize_unit(2, "MWh", "energy") == 2000.0
    assert normalize_unit(0.5, "MWh", "energy") == 500.0


def test_gwh_to_kwh_conversion():
    """GWh should convert to kWh correctly."""
    assert normalize_unit(1, "GWh", "energy") == 1000000.0


def test_kwh_passthrough():
    """kWh should pass through unchanged."""
    assert normalize_unit(100, "kWh", "energy") == 100.0
    assert normalize_unit(123.456, "kWh", "energy") == 123.456


def test_power_units():
    """Power units (W, kW, MW) should convert correctly."""
    assert normalize_unit(1000, "W", "power") == 1.0  # 1000 W = 1 kW
    assert normalize_unit(5, "kW", "power") == 5.0
    assert normalize_unit(2, "MW", "power") == 2000.0


def test_unsupported_unit_raises_error():
    """Unsupported units should raise ValueError."""
    with pytest.raises(ValueError, match="Unsupported unit"):
        normalize_unit(100, "BTU", "energy")
    
    with pytest.raises(ValueError, match="Unsupported unit"):
        normalize_unit(50, "joules", "energy")


def test_get_standard_unit():
    """Should return correct standard unit for metric type."""
    assert get_standard_unit("energy") == "kWh"
    assert get_standard_unit("power") == "kW"
    assert get_standard_unit("temperature") == "°C"
