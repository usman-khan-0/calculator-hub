import pytest

from app.calculators.gpa import Course, GPAError, calculate_gpa
from app.data.grade_scales import SCALE_4_0, SCALE_5_0, GradeScale


def test_basic_gpa_calculation():
    courses = [Course("Math", 3, "A")]
    result = calculate_gpa(courses, SCALE_4_0)
    assert result.gpa == 4.0
    assert result.total_credits == 3


def test_multiple_courses():
    courses = [
        Course("Mathematics", 3, "A"),
        Course("Physics", 4, "B+"),
        Course("English", 3, "A-"),
    ]
    result = calculate_gpa(courses, SCALE_4_0)
    expected_points = 3 * 4.0 + 4 * 3.3 + 3 * 3.7
    expected_credits = 10
    assert result.total_credits == expected_credits
    assert result.gpa == pytest.approx(expected_points / expected_credits, abs=1e-4)


def test_different_credit_hours():
    courses = [Course("A", 1, "A"), Course("B", 6, "F")]
    result = calculate_gpa(courses, SCALE_4_0)
    assert result.total_credits == 7
    assert result.gpa == pytest.approx((1 * 4.0 + 6 * 0.0) / 7, abs=1e-4)


def test_different_grading_scales():
    courses = [Course("A", 3, "A+")]
    result_4 = calculate_gpa(courses, SCALE_4_0)
    result_5 = calculate_gpa(courses, SCALE_5_0)
    assert result_4.gpa == 4.0
    assert result_5.gpa == 5.0


def test_invalid_grade_raises():
    courses = [Course("A", 3, "Z")]
    with pytest.raises(GPAError):
        calculate_gpa(courses, SCALE_4_0)


def test_zero_credits_raises():
    with pytest.raises(GPAError):
        Course("A", 0, "A")


def test_no_courses_raises():
    with pytest.raises(GPAError):
        calculate_gpa([], SCALE_4_0)


def test_custom_scale_extensibility():
    custom = GradeScale(name="Custom", max_points=4.3, grades={"A++": 4.3, "F": 0.0})
    courses = [Course("A", 3, "A++")]
    result = calculate_gpa(courses, custom)
    assert result.gpa == 4.3
