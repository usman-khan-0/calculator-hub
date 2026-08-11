"""Percentage calculator engine: covers the four common operations."""

from __future__ import annotations

from dataclasses import dataclass


class PercentageError(Exception):
    """Raised for invalid percentage calculation input."""


def percentage_of(percent: float, value: float) -> float:
    """What is X% of Y?"""
    return (percent / 100.0) * value


def what_percentage(part: float, whole: float) -> float:
    """X is what percentage of Y?"""
    if whole == 0:
        raise PercentageError("The base value cannot be zero")
    return (part / whole) * 100.0


@dataclass
class PercentageChangeResult:
    difference: float
    percent_change: float
    increased: bool


def percentage_change(old_value: float, new_value: float) -> PercentageChangeResult:
    """Percentage increase/decrease from old_value to new_value."""
    if old_value == 0:
        raise PercentageError("Old value cannot be zero")
    difference = new_value - old_value
    percent = (difference / old_value) * 100.0
    return PercentageChangeResult(
        difference=difference,
        percent_change=round(abs(percent), 4),
        increased=difference >= 0,
    )


def reverse_percentage(part: float, percent: float) -> float:
    """If `part` is `percent`% of some whole, find the whole."""
    if percent == 0:
        raise PercentageError("Percentage cannot be zero")
    return part / (percent / 100.0)


__all__ = [
    "PercentageError",
    "percentage_of",
    "what_percentage",
    "percentage_change",
    "PercentageChangeResult",
    "reverse_percentage",
]
