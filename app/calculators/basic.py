"""Simple/basic calculator engine.

Wraps :mod:`app.utils.calculations` with a small state machine suitable
for a standard four-function calculator with parentheses, percent, and
plus/minus.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.utils.calculations import CalculationError, ExpressionEvaluator, format_result


@dataclass
class BasicCalculator:
    """Stateful basic calculator: tracks the current expression and Ans."""

    expression: str = ""
    ans: float = 0.0

    def append(self, token: str) -> str:
        self.expression += token
        return self.expression

    def backspace(self) -> str:
        self.expression = self.expression[:-1]
        return self.expression

    def clear(self) -> str:
        self.expression = ""
        return self.expression

    def toggle_sign(self) -> str:
        """Wrap the whole current expression in a unary minus (or unwrap)."""
        text = self.expression.strip()
        if not text:
            return self.expression
        if text.startswith("-(") and text.endswith(")"):
            self.expression = text[2:-1]
        else:
            self.expression = f"-({text})"
        return self.expression

    def equals(self) -> float:
        evaluator = ExpressionEvaluator(degrees=True, ans=self.ans)
        result = evaluator.evaluate(self.expression)
        self.ans = result
        self.expression = format_result(result)
        return result


def calculate(expression: str, ans: float = 0.0) -> float:
    """Stateless helper: evaluate ``expression`` and return the result."""
    return ExpressionEvaluator(degrees=True, ans=ans).evaluate(expression)


__all__ = ["BasicCalculator", "calculate", "CalculationError"]
