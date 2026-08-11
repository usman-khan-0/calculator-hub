"""Reusable card component used on the Home screen to represent a
single calculator entry (icon + title + subtitle)."""

from __future__ import annotations

from kivy.properties import StringProperty
from kivymd.uix.card import MDCard


class CalculatorCard(MDCard):
    """A tappable Material card representing one calculator.

    Attributes are bound from Python when cards are generated
    dynamically on the Home screen (see ``home_screen.py``).
    """

    title_text = StringProperty("")
    subtitle_text = StringProperty("")
    icon_name = StringProperty("calculator-variant")
    screen_name = StringProperty("")
