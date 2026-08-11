"""Modular unit converter.

Each category maps a unit name to a factor relative to a chosen base
unit (e.g. meters for length). Temperature is handled specially since
it requires an affine (not purely multiplicative) conversion. New units
or categories can be added by extending ``_CATEGORIES``/``_TEMPERATURE``
without touching the conversion function itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List, Tuple


class UnitConversionError(Exception):
    """Raised for unknown units/categories or invalid input."""


# Factors are "how many base units in 1 of this unit".
_CATEGORIES: Dict[str, Dict[str, float]] = {
    "Length": {
        "Meters": 1.0,
        "Kilometers": 1000.0,
        "Centimeters": 0.01,
        "Millimeters": 0.001,
        "Miles": 1609.344,
        "Yards": 0.9144,
        "Feet": 0.3048,
        "Inches": 0.0254,
        "Nautical Miles": 1852.0,
    },
    "Weight": {
        "Kilograms": 1.0,
        "Grams": 0.001,
        "Milligrams": 0.000001,
        "Pounds": 0.45359237,
        "Ounces": 0.028349523125,
        "Metric Tons": 1000.0,
        "Stone": 6.35029318,
    },
    "Area": {
        "Square Meters": 1.0,
        "Square Kilometers": 1_000_000.0,
        "Square Feet": 0.09290304,
        "Square Yards": 0.83612736,
        "Acres": 4046.8564224,
        "Hectares": 10000.0,
    },
    "Volume": {
        "Liters": 1.0,
        "Milliliters": 0.001,
        "Cubic Meters": 1000.0,
        "Gallons (US)": 3.785411784,
        "Quarts (US)": 0.946352946,
        "Pints (US)": 0.473176473,
        "Cups": 0.2365882365,
        "Fluid Ounces (US)": 0.0295735295625,
    },
    "Time": {
        "Seconds": 1.0,
        "Minutes": 60.0,
        "Hours": 3600.0,
        "Days": 86400.0,
        "Weeks": 604800.0,
        "Milliseconds": 0.001,
    },
    "Speed": {
        "Meters/second": 1.0,
        "Kilometers/hour": 0.277777778,
        "Miles/hour": 0.44704,
        "Knots": 0.514444444,
        "Feet/second": 0.3048,
    },
    "Data Storage": {
        "Bytes": 1.0,
        "Kilobytes": 1024.0,
        "Megabytes": 1024.0 ** 2,
        "Gigabytes": 1024.0 ** 3,
        "Terabytes": 1024.0 ** 4,
        "Bits": 0.125,
    },
}


def _celsius_to_c(value: float, from_unit: str) -> float:
    if from_unit == "Celsius":
        return value
    if from_unit == "Fahrenheit":
        return (value - 32.0) * 5.0 / 9.0
    if from_unit == "Kelvin":
        return value - 273.15
    raise UnitConversionError(f"Unknown temperature unit: {from_unit}")


def _c_to_target(celsius: float, to_unit: str) -> float:
    if to_unit == "Celsius":
        return celsius
    if to_unit == "Fahrenheit":
        return celsius * 9.0 / 5.0 + 32.0
    if to_unit == "Kelvin":
        return celsius + 273.15
    raise UnitConversionError(f"Unknown temperature unit: {to_unit}")


_TEMPERATURE_UNITS: Tuple[str, ...] = ("Celsius", "Fahrenheit", "Kelvin")


def categories() -> List[str]:
    return list(_CATEGORIES.keys()) + ["Temperature"]


def units_for(category: str) -> List[str]:
    if category == "Temperature":
        return list(_TEMPERATURE_UNITS)
    if category not in _CATEGORIES:
        raise UnitConversionError(f"Unknown category: {category}")
    return list(_CATEGORIES[category].keys())


def convert(category: str, value: float, from_unit: str, to_unit: str) -> float:
    if category == "Temperature":
        celsius = _celsius_to_c(value, from_unit)
        result = _c_to_target(celsius, to_unit)
        return round(result, 6)

    if category not in _CATEGORIES:
        raise UnitConversionError(f"Unknown category: {category}")
    units = _CATEGORIES[category]
    if from_unit not in units:
        raise UnitConversionError(f"Unknown unit '{from_unit}' in {category}")
    if to_unit not in units:
        raise UnitConversionError(f"Unknown unit '{to_unit}' in {category}")

    base_value = value * units[from_unit]
    result = base_value / units[to_unit]
    return round(result, 8)


def register_unit(category: str, unit_name: str, factor_to_base: float) -> None:
    """Add a new unit to an existing (non-temperature) category."""
    if category not in _CATEGORIES:
        _CATEGORIES[category] = {}
    _CATEGORIES[category][unit_name] = factor_to_base


__all__ = [
    "UnitConversionError",
    "categories",
    "units_for",
    "convert",
    "register_unit",
]
