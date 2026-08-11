"""Average calculator engine: mean, sum, count, median, and mode."""

from __future__ import annotations

import statistics
from dataclasses import dataclass
from typing import List


class AverageError(Exception):
    """Raised when there is no valid data to average."""


@dataclass
class AverageResult:
    count: int
    total: float
    mean: float
    median: float
    mode: List[float]


def calculate_average(numbers: List[float]) -> AverageResult:
    if not numbers:
        raise AverageError("Add at least one number")

    total = sum(numbers)
    count = len(numbers)
    mean = total / count
    median = statistics.median(numbers)

    try:
        modes = statistics.multimode(numbers)
    except AttributeError:
        # Python < 3.8 fallback (multimode added in 3.8).
        try:
            modes = [statistics.mode(numbers)]
        except statistics.StatisticsError:
            modes = []

    # If every value is unique, report no distinct mode (all values tie).
    if len(modes) == count:
        modes = []

    return AverageResult(
        count=count,
        total=round(total, 6),
        mean=round(mean, 6),
        median=round(median, 6),
        mode=[round(m, 6) for m in modes],
    )


__all__ = ["AverageResult", "AverageError", "calculate_average"]
