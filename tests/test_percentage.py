import pytest

from app.calculators.percentage import (
    PercentageError,
    percentage_change,
    percentage_of,
    reverse_percentage,
    what_percentage,
)


def test_percentage_of():
    assert percentage_of(20, 500) == 100


def test_what_percentage():
    assert what_percentage(50, 200) == 25


def test_what_percentage_zero_base_raises():
    with pytest.raises(PercentageError):
        what_percentage(10, 0)


def test_percentage_increase():
    result = percentage_change(100, 125)
    assert result.percent_change == 25
    assert result.increased is True


def test_percentage_decrease():
    result = percentage_change(100, 80)
    assert result.percent_change == 20
    assert result.increased is False


def test_reverse_percentage():
    # 100 is 25% of what number? -> 400
    assert reverse_percentage(100, 25) == 400
