"""CGPA (Cumulative GPA) calculation engine across multiple semesters."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.calculators.gpa import GPAError


@dataclass
class SemesterRecord:
    label: str
    gpa: float
    credit_hours: float

    def __post_init__(self) -> None:
        if self.credit_hours <= 0:
            raise GPAError(f"Credit hours for '{self.label}' must be greater than zero")
        if self.gpa < 0:
            raise GPAError(f"GPA for '{self.label}' cannot be negative")


@dataclass
class CGPAResult:
    total_credits: float
    total_grade_points: float
    cgpa: float


def calculate_cgpa(semesters: List[SemesterRecord]) -> CGPAResult:
    """CGPA = sum(GPA_i * credits_i) / sum(credits_i)."""
    if not semesters:
        raise GPAError("Add at least one semester to calculate CGPA")

    total_credits = 0.0
    total_points = 0.0
    for semester in semesters:
        total_credits += semester.credit_hours
        total_points += semester.gpa * semester.credit_hours

    if total_credits == 0:
        raise GPAError("Total credit hours cannot be zero")

    cgpa = total_points / total_credits
    return CGPAResult(total_credits=total_credits, total_grade_points=round(total_points, 4), cgpa=round(cgpa, 4))


@dataclass
class CGPACalculatorState:
    semesters: List[SemesterRecord] = field(default_factory=list)

    def add_semester(self, label: str, gpa: float, credit_hours: float) -> None:
        self.semesters.append(SemesterRecord(label=label, gpa=gpa, credit_hours=credit_hours))

    def remove_semester(self, index: int) -> None:
        if 0 <= index < len(self.semesters):
            self.semesters.pop(index)

    def clear(self) -> None:
        self.semesters.clear()

    def calculate(self) -> CGPAResult:
        return calculate_cgpa(self.semesters)


__all__ = ["SemesterRecord", "CGPAResult", "calculate_cgpa", "CGPACalculatorState"]
