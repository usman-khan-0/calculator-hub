"""Reusable calculator button widgets."""

from __future__ import annotations

from kivymd.uix.button import MDRaisedButton


class CalculatorButton(MDRaisedButton):
    """A large, rounded calculator keypad button.

    Sizing, radius, and elevation are defined in ``kv/calculator.kv`` so
    this class only needs to exist for identification/styling in KV
    rules (``<CalculatorButton>``).
    """
