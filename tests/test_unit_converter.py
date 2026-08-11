import pytest

from app.calculators.unit_converter import UnitConversionError, convert


def test_meters_to_feet():
    assert convert("Length", 1, "Meters", "Feet") == pytest.approx(3.28084, abs=1e-4)


def test_km_to_miles():
    assert convert("Length", 1, "Kilometers", "Miles") == pytest.approx(0.621371, abs=1e-4)


def test_kg_to_pounds():
    assert convert("Weight", 1, "Kilograms", "Pounds") == pytest.approx(2.20462, abs=1e-4)


def test_celsius_to_fahrenheit():
    assert convert("Temperature", 0, "Celsius", "Fahrenheit") == 32
    assert convert("Temperature", 100, "Celsius", "Fahrenheit") == 212


def test_fahrenheit_to_celsius():
    assert convert("Temperature", 32, "Fahrenheit", "Celsius") == 0


def test_mb_to_gb():
    assert convert("Data Storage", 1024, "Megabytes", "Gigabytes") == pytest.approx(1.0)


def test_unknown_category_raises():
    with pytest.raises(UnitConversionError):
        convert("Nonsense", 1, "A", "B")


def test_unknown_unit_raises():
    with pytest.raises(UnitConversionError):
        convert("Length", 1, "Meters", "Furlongs")
