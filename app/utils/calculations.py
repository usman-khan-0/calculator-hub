"""Safe mathematical expression evaluation.

This module implements a restricted expression evaluator built on Python's
``ast`` module. It intentionally avoids ``eval()``/``exec()`` on user input.
Only a whitelist of AST node types, operators, and function/constant names
is permitted; anything else raises :class:`CalculationError`.

The evaluator is used by both the Simple Calculator and the Scientific
Calculator, and supports two angle modes (degrees/radians) for trig
functions.
"""

from __future__ import annotations

import ast
import math
import operator
from dataclasses import dataclass, field
from typing import Callable, Dict, List


class CalculationError(Exception):
    """Raised for any invalid, unsafe, or unevaluable expression."""


# ---------------------------------------------------------------------------
# Allowed operators
# ---------------------------------------------------------------------------

_BIN_OPS: Dict[type, Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
    ast.FloorDiv: operator.floordiv,
}

_UNARY_OPS: Dict[type, Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_MAX_RESULT_MAGNITUDE = 1e300
_MAX_INPUT_LENGTH = 500


def _factorial(x: float) -> float:
    if x < 0 or x != int(x):
        raise CalculationError("Factorial is only defined for non-negative integers")
    if x > 170:
        raise CalculationError("Overflow: number too large for factorial")
    return float(math.factorial(int(x)))


def _safe_sqrt(x: float) -> float:
    if x < 0:
        raise CalculationError("Cannot take square root of a negative number")
    return math.sqrt(x)


def _safe_log(x: float) -> float:
    if x <= 0:
        raise CalculationError("Logarithm is only defined for positive numbers")
    return math.log10(x)


def _safe_ln(x: float) -> float:
    if x <= 0:
        raise CalculationError("Natural log is only defined for positive numbers")
    return math.log(x)


def _reciprocal(x: float) -> float:
    if x == 0:
        raise CalculationError("Cannot divide by zero")
    return 1.0 / x


@dataclass
class AngleAwareFunctions:
    """Builds a function table whose trig functions respect an angle mode."""

    degrees: bool = True

    def _to_rad(self, x: float) -> float:
        return math.radians(x) if self.degrees else x

    def _from_rad(self, x: float) -> float:
        return math.degrees(x) if self.degrees else x

    def table(self) -> Dict[str, Callable[..., float]]:
        return {
            "sin": lambda x: math.sin(self._to_rad(x)),
            "cos": lambda x: math.cos(self._to_rad(x)),
            "tan": lambda x: math.tan(self._to_rad(x)),
            "asin": lambda x: self._from_rad(math.asin(x)) if -1 <= x <= 1 else _raise("asin domain is [-1, 1]"),
            "acos": lambda x: self._from_rad(math.acos(x)) if -1 <= x <= 1 else _raise("acos domain is [-1, 1]"),
            "atan": lambda x: self._from_rad(math.atan(x)),
            "sinh": math.sinh,
            "cosh": math.cosh,
            "tanh": math.tanh,
            "log": _safe_log,
            "log10": _safe_log,
            "ln": _safe_ln,
            "sqrt": _safe_sqrt,
            "cbrt": lambda x: math.copysign(abs(x) ** (1 / 3), x),
            "abs": abs,
            "fact": _factorial,
            "factorial": _factorial,
            "recip": _reciprocal,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
        }


def _raise(message: str):
    raise CalculationError(message)


_CONSTANTS: Dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}


@dataclass
class ExpressionEvaluator:
    """Evaluates a restricted arithmetic/scientific expression safely.

    Parameters
    ----------
    degrees:
        When True, trigonometric functions interpret/produce angles in
        degrees. When False, radians are used.
    ans:
        The previous answer, made available to expressions as the token
        ``Ans``.
    memory:
        The current value of calculator memory, available as ``M``.
    """

    degrees: bool = True
    ans: float = 0.0
    memory: float = 0.0
    _functions: Dict[str, Callable[..., float]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._functions = AngleAwareFunctions(degrees=self.degrees).table()

    def evaluate(self, expression: str) -> float:
        """Evaluate ``expression`` and return a float result.

        Raises :class:`CalculationError` on any invalid or unsafe input.
        """
        if not expression or not expression.strip():
            raise CalculationError("Expression is empty")
        if len(expression) > _MAX_INPUT_LENGTH:
            raise CalculationError("Expression is too long")

        normalized = self._normalize(expression)

        try:
            tree = ast.parse(normalized, mode="eval")
        except (SyntaxError, ValueError) as exc:
            raise CalculationError("Invalid expression") from exc

        result = self._eval_node(tree.body)

        if isinstance(result, complex):
            raise CalculationError("Result is not a real number")

        try:
            result = float(result)
        except OverflowError as exc:
            raise CalculationError("Overflow: result is too large") from exc

        if math.isnan(result):
            raise CalculationError("Result is undefined (NaN)")
        if math.isinf(result) or abs(result) > _MAX_RESULT_MAGNITUDE:
            raise CalculationError("Overflow: result is too large")
        return result

    # -- normalization -----------------------------------------------------
    def _normalize(self, expression: str) -> str:
        replacements = {
            "×": "*",
            "÷": "/",
            "^": "**",
            "π": "pi",
            "√": "sqrt",
            "%": "/100",
        }
        text = expression
        for old, new in replacements.items():
            text = text.replace(old, new)

        # Replace whole-word tokens 'Ans' and standalone 'M' (memory) exactly
        # once, using regex word boundaries so we never double-substitute.
        import re

        text = re.sub(r"\bAns\b", "__ans__", text)
        text = re.sub(r"\bM\b", "__mem__", text)
        return text

    # -- evaluation ---------------------------------------------------------
    def _eval_node(self, node: ast.AST):
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body)

        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculationError("Invalid literal in expression")

        if isinstance(node, ast.BinOp):
            op_type = type(node.op)
            if op_type not in _BIN_OPS:
                raise CalculationError("Unsupported operator")
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)
            if op_type in (ast.Div, ast.Mod, ast.FloorDiv) and right == 0:
                raise CalculationError("Division by zero")
            try:
                return _BIN_OPS[op_type](left, right)
            except OverflowError as exc:
                raise CalculationError("Overflow: result is too large") from exc

        if isinstance(node, ast.UnaryOp):
            op_type = type(node.op)
            if op_type not in _UNARY_OPS:
                raise CalculationError("Unsupported unary operator")
            return _UNARY_OPS[op_type](self._eval_node(node.operand))

        if isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise CalculationError("Unsupported function call")
            func_name = node.func.id
            if func_name not in self._functions:
                raise CalculationError(f"Unknown function: {func_name}")
            if node.keywords:
                raise CalculationError("Keyword arguments are not supported")
            args = [self._eval_node(arg) for arg in node.args]
            try:
                return self._functions[func_name](*args)
            except CalculationError:
                raise
            except (ValueError, TypeError, OverflowError) as exc:
                raise CalculationError(f"Invalid input for {func_name}") from exc

        if isinstance(node, ast.Name):
            if node.id == "__ans__":
                return self.ans
            if node.id == "__mem__":
                return self.memory
            if node.id in _CONSTANTS:
                return _CONSTANTS[node.id]
            raise CalculationError(f"Unknown identifier: {node.id}")

        raise CalculationError("Unsupported expression syntax")


def evaluate_expression(expression: str, degrees: bool = True, ans: float = 0.0, memory: float = 0.0) -> float:
    """Convenience function wrapping :class:`ExpressionEvaluator`."""
    return ExpressionEvaluator(degrees=degrees, ans=ans, memory=memory).evaluate(expression)


def power(base: float, exponent: float) -> float:
    """x^y with overflow protection."""
    try:
        result = base ** exponent
    except OverflowError as exc:
        raise CalculationError("Overflow: result is too large") from exc
    if isinstance(result, complex):
        raise CalculationError("Result is not a real number")
    if abs(result) > _MAX_RESULT_MAGNITUDE:
        raise CalculationError("Overflow: result is too large")
    return float(result)


def square(x: float) -> float:
    return power(x, 2)


def cube(x: float) -> float:
    return power(x, 3)


def power_of_ten(x: float) -> float:
    return power(10.0, x)


def exp_of(x: float) -> float:
    try:
        return math.exp(x)
    except OverflowError as exc:
        raise CalculationError("Overflow: result is too large") from exc


def to_fraction_string(value: float, max_denominator: int = 10000) -> str:
    """Convert a float to an approximate fraction string 'n/d'."""
    from fractions import Fraction

    frac = Fraction(value).limit_denominator(max_denominator)
    if frac.denominator == 1:
        return str(frac.numerator)
    return f"{frac.numerator}/{frac.denominator}"


def format_result(value: float, precision: int = 6) -> str:
    """Format a numeric result for display, trimming trailing zeros."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    formatted = f"{value:.{precision}f}"
    formatted = formatted.rstrip("0").rstrip(".")
    return formatted if formatted else "0"


__all__: List[str] = [
    "CalculationError",
    "ExpressionEvaluator",
    "evaluate_expression",
    "power",
    "square",
    "cube",
    "power_of_ten",
    "exp_of",
    "to_fraction_string",
    "format_result",
]
