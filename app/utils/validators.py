"""Reusable input validation helpers.

These functions raise :class:`ValidationError` with a human-readable
message so the UI layer can surface it directly in a dialog or snackbar.
"""

from __future__ import annotations

from typing import Optional

_MAX_NUMBER = 1e15


class ValidationError(Exception):
    """Raised when user-supplied input fails validation."""


def require_non_empty(value: Optional[str], field_name: str = "This field") -> str:
    if value is None or str(value).strip() == "":
        raise ValidationError(f"{field_name} cannot be empty")
    return str(value).strip()


def parse_float(value: Optional[str], field_name: str = "Value") -> float:
    text = require_non_empty(value, field_name)
    try:
        number = float(text)
    except ValueError as exc:
        raise ValidationError(f"{field_name} must be a valid number") from exc
    if number != number:  # NaN check
        raise ValidationError(f"{field_name} is not a valid number")
    if abs(number) > _MAX_NUMBER:
        raise ValidationError(f"{field_name} is too large")
    return number


def parse_positive_float(value: Optional[str], field_name: str = "Value") -> float:
    number = parse_float(value, field_name)
    if number <= 0:
        raise ValidationError(f"{field_name} must be greater than zero")
    return number


def parse_non_negative_float(value: Optional[str], field_name: str = "Value") -> float:
    number = parse_float(value, field_name)
    if number < 0:
        raise ValidationError(f"{field_name} cannot be negative")
    return number


def parse_credit_hours(value: Optional[str]) -> float:
    hours = parse_non_negative_float(value, "Credit hours")
    if hours == 0:
        raise ValidationError("Credit hours must be greater than zero")
    if hours > 30:
        raise ValidationError("Credit hours seems unrealistically high")
    return hours


def parse_marks(value: Optional[str], field_name: str = "Marks") -> float:
    return parse_non_negative_float(value, field_name)


def validate_obtained_marks(obtained: float, total: float) -> None:
    if total <= 0:
        raise ValidationError("Total marks must be greater than zero")
    if obtained < 0:
        raise ValidationError("Obtained marks cannot be negative")
    if obtained > total:
        raise ValidationError("Obtained marks cannot exceed total marks")


def validate_course_name(name: Optional[str]) -> str:
    text = require_non_empty(name, "Course name")
    if len(text) > 100:
        raise ValidationError("Course name is too long")
    return text
