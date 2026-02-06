"""Unit conversion utilities for energy and power measurements."""
from typing import Dict


# Conversion factors to standard units
# Energy: convert to kWh
# Power: convert to kW
UNIT_CONVERSIONS: Dict[str, float] = {
    # Energy units (to kWh)
    "kWh": 1.0,
    "Wh": 0.001,          # 1000 Wh = 1 kWh
    "MWh": 1000.0,        # 1 MWh = 1000 kWh
    "GWh": 1000000.0,     # 1 GWh = 1,000,000 kWh
    
    # Power units (to kW)
    "kW": 1.0,
    "W": 0.001,           # 1000 W = 1 kW
    "MW": 1000.0,         # 1 MW = 1000 kW
    "GW": 1000000.0,      # 1 GW = 1,000,000 kW
}


def normalize_unit(value: float, from_unit: str, metric_type: str = "energy") -> float:
    """
    Convert value to standard unit (kWh for energy, kW for power).
    
    Args:
        value: The numeric value to convert
        from_unit: Original unit (e.g., "Wh", "MWh", "kW")
        metric_type: Type of metric ("energy" or "power") - for documentation
        
    Returns:
        Converted value in standard unit (kWh or kW)
        
    Raises:
        ValueError: If unit is not supported
        
    Examples:
        >>> normalize_unit(5000, "Wh", "energy")
        5.0
        >>> normalize_unit(2, "MWh", "energy")
        2000.0
        >>> normalize_unit(1500, "W", "power")
        1.5
    """
    if from_unit not in UNIT_CONVERSIONS:
        raise ValueError(
            f"Unsupported unit: {from_unit}. "
            f"Supported units: {', '.join(UNIT_CONVERSIONS.keys())}"
        )
    
    conversion_factor = UNIT_CONVERSIONS[from_unit]
    return value * conversion_factor


def get_standard_unit(metric_type: str) -> str:
    """
    Get the standard unit for a metric type.
    
    Args:
        metric_type: Type of metric ("energy", "power", etc.)
        
    Returns:
        Standard unit string
        
    Examples:
        >>> get_standard_unit("energy")
        'kWh'
        >>> get_standard_unit("power")
        'kW'
    """
    standard_units = {
        "energy": "kWh",
        "power": "kW",
        "temperature": "°C",  # For future expansion
    }
    
    return standard_units.get(metric_type, "unknown")
