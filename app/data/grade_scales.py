"""Configurable GPA grade scales and grade-boundary presets.

New university grading systems can be added here (or registered at
runtime with :func:`register_scale`) without touching the GPA
calculation engine in ``app/calculators/gpa.py``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass(frozen=True)
class GradeScale:
    """A named mapping of letter grades to grade-point values."""

    name: str
    grades: Dict[str, float] = field(default_factory=dict)
    max_points: float = 4.0

    def points_for(self, grade: str) -> float:
        key = grade.strip().upper()
        if key not in self.grades:
            raise KeyError(f"Grade '{grade}' is not defined in scale '{self.name}'")
        return self.grades[key]

    def grade_letters(self) -> List[str]:
        # Preserve a sensible display order (highest to lowest points).
        return sorted(self.grades, key=lambda g: self.grades[g], reverse=True)


SCALE_4_0 = GradeScale(
    name="4.0 Scale",
    max_points=4.0,
    grades={
        "A+": 4.0,
        "A": 4.0,
        "A-": 3.7,
        "B+": 3.3,
        "B": 3.0,
        "B-": 2.7,
        "C+": 2.3,
        "C": 2.0,
        "C-": 1.7,
        "D+": 1.3,
        "D": 1.0,
        "D-": 0.7,
        "F": 0.0,
    },
)

SCALE_5_0 = GradeScale(
    name="5.0 Scale",
    max_points=5.0,
    grades={
        "A+": 5.0,
        "A": 4.5,
        "B+": 4.0,
        "B": 3.5,
        "C+": 3.0,
        "C": 2.5,
        "D+": 2.0,
        "D": 1.5,
        "E": 1.0,
        "F": 0.0,
    },
)

SCALE_10_0 = GradeScale(
    name="10.0 Scale",
    max_points=10.0,
    grades={
        "O": 10.0,
        "A+": 9.0,
        "A": 8.0,
        "B+": 7.0,
        "B": 6.0,
        "C": 5.0,
        "P": 4.0,
        "F": 0.0,
    },
)

SCALE_PERCENTAGE = GradeScale(
    name="Percentage-based",
    max_points=100.0,
    grades={
        "90-100": 95.0,
        "80-89": 85.0,
        "70-79": 75.0,
        "60-69": 65.0,
        "50-59": 55.0,
        "0-49": 25.0,
    },
)

_REGISTRY: Dict[str, GradeScale] = {
    scale.name: scale
    for scale in (SCALE_4_0, SCALE_5_0, SCALE_10_0, SCALE_PERCENTAGE)
}


def register_scale(scale: GradeScale) -> None:
    """Add a new grading scale at runtime (e.g. a specific university's)."""
    _REGISTRY[scale.name] = scale


def get_scale(name: str) -> GradeScale:
    if name not in _REGISTRY:
        raise KeyError(f"Unknown grading scale: {name}")
    return _REGISTRY[name]


def available_scales() -> List[str]:
    return list(_REGISTRY.keys())


def default_scale() -> GradeScale:
    return SCALE_4_0


@dataclass(frozen=True)
class GradeBoundary:
    """A single (min_percentage, max_percentage) -> letter/point mapping."""

    label: str
    min_percentage: float
    max_percentage: float
    grade_point: float


@dataclass(frozen=True)
class GradeBoundaryTable:
    """An ordered, configurable set of percentage -> grade boundaries."""

    name: str
    boundaries: List[GradeBoundary]

    def grade_for(self, percentage: float) -> GradeBoundary:
        for boundary in self.boundaries:
            if boundary.min_percentage <= percentage <= boundary.max_percentage:
                return boundary
        # Fall back to the lowest boundary if nothing matched (e.g. negative).
        return self.boundaries[-1]


DEFAULT_GRADE_BOUNDARIES = GradeBoundaryTable(
    name="Standard",
    boundaries=[
        GradeBoundary("A+", 90, 100, 4.0),
        GradeBoundary("A", 80, 89.999, 4.0),
        GradeBoundary("B", 70, 79.999, 3.0),
        GradeBoundary("C", 60, 69.999, 2.0),
        GradeBoundary("D", 50, 59.999, 1.0),
        GradeBoundary("F", 0, 49.999, 0.0),
    ],
)

STRICT_GRADE_BOUNDARIES = GradeBoundaryTable(
    name="Strict",
    boundaries=[
        GradeBoundary("A+", 95, 100, 4.0),
        GradeBoundary("A", 90, 94.999, 4.0),
        GradeBoundary("A-", 85, 89.999, 3.7),
        GradeBoundary("B+", 80, 84.999, 3.3),
        GradeBoundary("B", 75, 79.999, 3.0),
        GradeBoundary("B-", 70, 74.999, 2.7),
        GradeBoundary("C+", 65, 69.999, 2.3),
        GradeBoundary("C", 60, 64.999, 2.0),
        GradeBoundary("D", 50, 59.999, 1.0),
        GradeBoundary("F", 0, 49.999, 0.0),
    ],
)

_BOUNDARY_REGISTRY: Dict[str, GradeBoundaryTable] = {
    table.name: table for table in (DEFAULT_GRADE_BOUNDARIES, STRICT_GRADE_BOUNDARIES)
}


def register_boundary_table(table: GradeBoundaryTable) -> None:
    _BOUNDARY_REGISTRY[table.name] = table


def get_boundary_table(name: str) -> GradeBoundaryTable:
    if name not in _BOUNDARY_REGISTRY:
        raise KeyError(f"Unknown grade boundary table: {name}")
    return _BOUNDARY_REGISTRY[name]


def available_boundary_tables() -> List[str]:
    return list(_BOUNDARY_REGISTRY.keys())
