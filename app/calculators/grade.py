"""Grade calculator: converts marks into a percentage, letter grade, and
grade point using a configurable :class:`GradeBoundaryTable`.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.data.grade_scales import DEFAULT_GRADE_BOUNDARIES, GradeBoundaryTable


class GradeCalculationError(Exception):
    """Raised for invalid grade calculation input."""


@dataclass
class GradeResult:
    percentage: float
    grade: str
    grade_point: float


def calculate_grade(
    obtained_marks: float,
    total_marks: float,
    boundary_table: GradeBoundaryTable = None,
) -> GradeResult:
    if total_marks <= 0:
        raise GradeCalculationError("Total marks must be greater than zero")
    if obtained_marks < 0:
        raise GradeCalculationError("Obtained marks cannot be negative")
    if obtained_marks > total_marks:
        raise GradeCalculationError("Obtained marks cannot exceed total marks")

    table = boundary_table or DEFAULT_GRADE_BOUNDARIES
    percentage = round((obtained_marks / total_marks) * 100.0, 2)
    boundary = table.grade_for(percentage)
    return GradeResult(percentage=percentage, grade=boundary.label, grade_point=boundary.grade_point)


__all__ = ["GradeResult", "GradeCalculationError", "calculate_grade"]
