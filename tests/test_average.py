import pytest

from app.calculators.average import AverageError, calculate_average


def test_basic_average():
    result = calculate_average([10, 20, 30, 40])
    assert result.mean == 25
    assert result.total == 100
    assert result.count == 4


def test_median_odd():
    result = calculate_average([1, 3, 2])
    assert result.median == 2


def test_median_even():
    result = calculate_average([1, 2, 3, 4])
    assert result.median == 2.5


def test_mode():
    result = calculate_average([1, 2, 2, 3])
    assert result.mode == [2]


def test_empty_raises():
    with pytest.raises(AverageError):
        calculate_average([])
