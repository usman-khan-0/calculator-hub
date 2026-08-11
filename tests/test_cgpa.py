import pytest

from app.calculators.cgpa import SemesterRecord, calculate_cgpa
from app.calculators.gpa import GPAError


def test_single_semester():
    result = calculate_cgpa([SemesterRecord("S1", 3.5, 15)])
    assert result.cgpa == 3.5


def test_multiple_semesters_weighted():
    semesters = [
        SemesterRecord("S1", 3.5, 15),
        SemesterRecord("S2", 3.0, 18),
    ]
    result = calculate_cgpa(semesters)
    expected = (3.5 * 15 + 3.0 * 18) / (15 + 18)
    assert result.cgpa == pytest.approx(expected, abs=1e-4)


def test_invalid_negative_gpa():
    with pytest.raises(GPAError):
        SemesterRecord("S1", -1.0, 15)


def test_invalid_zero_credits():
    with pytest.raises(GPAError):
        SemesterRecord("S1", 3.0, 0)


def test_empty_semesters_raises():
    with pytest.raises(GPAError):
        calculate_cgpa([])
