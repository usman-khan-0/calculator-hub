import math

import pytest

from app.utils.calculations import CalculationError, evaluate_expression


def test_addition():
    assert evaluate_expression("2+3") == 5


def test_subtraction():
    assert evaluate_expression("10-4") == 6


def test_multiplication():
    assert evaluate_expression("6*7") == 42


def test_division():
    assert evaluate_expression("9/3") == 3


def test_division_by_zero():
    with pytest.raises(CalculationError):
        evaluate_expression("5/0")


def test_parentheses():
    assert evaluate_expression("12 + 5 * 3") == 27
    assert evaluate_expression("(12 + 5) * 3") == 51


def test_percent_symbol():
    # 50% -> 0.5
    assert evaluate_expression("50%") == 0.5


def test_unicode_operators():
    assert evaluate_expression("6×7") == 42
    assert evaluate_expression("12÷4") == 3


def test_invalid_expression():
    with pytest.raises(CalculationError):
        evaluate_expression("2 + * 3")


def test_empty_expression():
    with pytest.raises(CalculationError):
        evaluate_expression("")


def test_unsafe_input_rejected():
    with pytest.raises(CalculationError):
        evaluate_expression("__import__('os').system('echo hi')")


def test_name_error_rejected():
    with pytest.raises(CalculationError):
        evaluate_expression("os.system('ls')")


# -- scientific functions ------------------------------------------------

def test_sin_degrees():
    assert evaluate_expression("sin(90)", degrees=True) == pytest.approx(1.0)


def test_cos_degrees():
    assert evaluate_expression("cos(0)", degrees=True) == pytest.approx(1.0)


def test_tan_degrees():
    assert evaluate_expression("tan(45)", degrees=True) == pytest.approx(1.0)


def test_trig_radians():
    assert evaluate_expression("sin(pi/2)", degrees=False) == pytest.approx(1.0)


def test_sqrt():
    assert evaluate_expression("sqrt(16)") == 4


def test_sqrt_negative_raises():
    with pytest.raises(CalculationError):
        evaluate_expression("sqrt(-4)")


def test_log10():
    assert evaluate_expression("log(100)") == pytest.approx(2.0)


def test_ln():
    assert evaluate_expression("ln(e)") == pytest.approx(1.0)


def test_power():
    assert evaluate_expression("2^10") == 1024


def test_factorial():
    assert evaluate_expression("fact(5)") == 120


def test_factorial_negative_raises():
    with pytest.raises(CalculationError):
        evaluate_expression("fact(-1)")


def test_degree_radian_conversion_consistency():
    deg_result = evaluate_expression("sin(30)", degrees=True)
    rad_result = evaluate_expression("sin(pi/6)", degrees=False)
    assert deg_result == pytest.approx(rad_result, abs=1e-9)


def test_ans_reference():
    assert evaluate_expression("Ans+1", ans=10) == 11


def test_overflow_detection():
    with pytest.raises(CalculationError):
        evaluate_expression("10^400")
