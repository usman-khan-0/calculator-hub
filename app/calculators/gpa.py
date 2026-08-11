"""GPA calculation engine.

The engine receives a :class:`~app.data.grade_scales.GradeScale` as input
so new university grading systems can be plugged in without changing the
calculation algorithm (requirement #25 / #8).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.data.grade_scales import GradeScale, default_scale


class GPAError(Exception):
    """Raised for invalid GPA calculation input."""


@dataclass
class Course:
    name: str
    credit_hours: float
    grade: str

    def __post_init__(self) -> None:
        if self.credit_hours <= 0:
            raise GPAError(f"Credit hours for '{self.name}' must be greater than zero")


@dataclass
class GPAResult:
    total_credits: float
    total_grade_points: float
    gpa: float


def calculate_gpa(courses: List[Course], scale: GradeScale = None) -> GPAResult:
    """Compute GPA = sum(credits * grade_points) / sum(credits)."""
    if not courses:
        raise GPAError("Add at least one course to calculate GPA")

    scale = scale or default_scale()

    total_credits = 0.0
    total_points = 0.0
    for course in courses:
        try:
            points = scale.points_for(course.grade)
        except KeyError as exc:
            raise GPAError(str(exc)) from exc
        total_credits += course.credit_hours
        total_points += course.credit_hours * points

    if total_credits == 0:
        raise GPAError("Total credit hours cannot be zero")

    gpa = total_points / total_credits
    return GPAResult(total_credits=total_credits, total_grade_points=total_points, gpa=round(gpa, 4))


@dataclass
class GPACalculatorState:
    """Stateful wrapper used by the Semester GPA / GPA screens."""

    courses: List[Course] = field(default_factory=list)
    scale: GradeScale = field(default_factory=default_scale)

    def add_course(self, name: str, credit_hours: float, grade: str) -> None:
        self.courses.append(Course(name=name, credit_hours=credit_hours, grade=grade))

    def remove_course(self, index: int) -> None:
        if 0 <= index < len(self.courses):
            self.courses.pop(index)

    def clear(self) -> None:
        self.courses.clear()

    def calculate(self) -> GPAResult:
        return calculate_gpa(self.courses, self.scale)


__all__ = ["Course", "GPAResult", "GPAError", "calculate_gpa", "GPACalculatorState"]
