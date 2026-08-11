import pytest

from app.calculators.grade import GradeCalculationError, calculate_grade


def test_grade_a_plus():
    result = calculate_grade(95, 100)
    assert result.grade == "A+"
    assert result.percentage == 95.0


def test_grade_f():
    result = calculate_grade(30, 100)
    assert result.grade == "F"


def test_grade_boundary():
    result = calculate_grade(80, 100)
    assert result.grade == "A"


def test_total_marks_zero_raises():
    with pytest.raises(GradeCalculationError):
        calculate_grade(10, 0)


def test_obtained_exceeds_total_raises():
    with pytest.raises(GradeCalculationError):
        calculate_grade(120, 100)


def test_negative_obtained_raises():
    with pytest.raises(GradeCalculationError):
        calculate_grade(-5, 100)
