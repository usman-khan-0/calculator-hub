"""991ES-style scientific calculator engine.

This module implements the calculation/state logic only. It is entirely
independent of Kivy so it can be unit tested directly. The UI
(``app/screens/calculator_screen.py``) is responsible for wiring buttons
to these methods.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from app.utils.calculations import (
    CalculationError,
    ExpressionEvaluator,
    cube,
    exp_of,
    format_result,
    power,
    power_of_ten,
    square,
    to_fraction_string,
)


@dataclass
class HistoryEntry:
    expression: str
    result: str


@dataclass
class ScientificCalculator:
    """Stateful scientific calculator with memory, Ans, and DEG/RAD modes."""

    expression: str = ""
    ans: float = 0.0
    memory: float = 0.0
    degrees: bool = True
    history: List[HistoryEntry] = field(default_factory=list)
    max_history: int = 50

    # -- input editing -------------------------------------------------
    def append(self, token: str) -> str:
        self.expression += token
        return self.expression

    def backspace(self) -> str:
        self.expression = self.expression[:-1]
        return self.expression

    def clear(self) -> str:
        self.expression = ""
        return self.expression

    def clear_all(self) -> str:
        self.expression = ""
        self.ans = 0.0
        self.memory = 0.0
        self.history.clear()
        return self.expression

    # -- mode ------------------------------------------------------------
    def set_degree_mode(self, degrees: bool) -> None:
        self.degrees = degrees

    def toggle_mode(self) -> bool:
        self.degrees = not self.degrees
        return self.degrees

    # -- memory ------------------------------------------------------------
    def memory_add(self, value: float) -> float:
        self.memory += value
        return self.memory

    def memory_subtract(self, value: float) -> float:
        self.memory -= value
        return self.memory

    def memory_clear(self) -> float:
        self.memory = 0.0
        return self.memory

    def memory_recall(self) -> float:
        return self.memory

    # -- direct function shortcuts (buttons like x^2, x^3, 10^x, e^x) ----
    def apply_square(self) -> float:
        return self._apply_unary(square)

    def apply_cube(self) -> float:
        return self._apply_unary(cube)

    def apply_power_of_ten(self) -> float:
        return self._apply_unary(power_of_ten)

    def apply_exp(self) -> float:
        return self._apply_unary(exp_of)

    def _apply_unary(self, func) -> float:
        current = self.equals(record_history=False) if self.expression else self.ans
        result = func(current)
        self.expression = format_result(result)
        self.ans = result
        return result

    # -- evaluation -------------------------------------------------------
    def equals(self, record_history: bool = True) -> float:
        evaluator = ExpressionEvaluator(degrees=self.degrees, ans=self.ans, memory=self.memory)
        result = evaluator.evaluate(self.expression)
        if record_history:
            self.history.insert(0, HistoryEntry(expression=self.expression, result=format_result(result)))
            self.history = self.history[: self.max_history]
        self.ans = result
        self.expression = format_result(result)
        return result

    def as_fraction(self) -> str:
        return to_fraction_string(self.ans)


def calculate(expression: str, degrees: bool = True, ans: float = 0.0, memory: float = 0.0) -> float:
    return ExpressionEvaluator(degrees=degrees, ans=ans, memory=memory).evaluate(expression)


__all__ = ["ScientificCalculator", "HistoryEntry", "calculate", "CalculationError"]
