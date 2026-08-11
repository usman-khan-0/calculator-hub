"""Home screen: shows calculator categories as searchable Material cards."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from kivymd.uix.screen import MDScreen

from app.components.calculator_card import CalculatorCard


@dataclass
class CalculatorEntry:
    """Describes one calculator tile shown on the Home screen."""

    title: str
    subtitle: str
    icon: str
    screen_name: str
    category: str
    calculator_key: str


# Central registry of all calculators available in the app. Adding a new
# calculator later only requires appending an entry here (plus a Screen
# class + kv rule) -- no restructuring needed.
CALCULATOR_REGISTRY: List[CalculatorEntry] = [
    CalculatorEntry("Simple Calculator", "Everyday arithmetic", "calculator",
                     "simple_calculator", "Basic Calculators", "simple"),
    CalculatorEntry("Basic Math Calculator", "Quick four-function math", "calculator-variant",
                     "simple_calculator", "Basic Calculators", "simple"),
    CalculatorEntry("Percentage Calculator", "Percent of, change, reverse", "percent",
                     "percentage_calculator", "Basic Calculators", "percentage"),
    CalculatorEntry("Average Calculator", "Mean, median, mode", "chart-bell-curve",
                     "average_calculator", "Basic Calculators", "average"),
    CalculatorEntry("991ES Scientific Calculator", "Trig, log, powers, memory", "calculator-variant-outline",
                     "scientific_calculator", "Scientific", "scientific"),
    CalculatorEntry("GPA Calculator", "Course-by-course GPA", "school",
                     "gpa_calculator", "GPA & Education", "gpa"),
    CalculatorEntry("CGPA Calculator", "Multi-semester cumulative GPA", "school-outline",
                     "cgpa_calculator", "GPA & Education", "cgpa"),
    CalculatorEntry("Semester GPA", "Add courses for one semester", "book-open-variant",
                     "semester_gpa_calculator", "GPA & Education", "gpa"),
    CalculatorEntry("Cumulative GPA", "Combine semesters into a CGPA", "book-multiple",
                     "cumulative_gpa_calculator", "GPA & Education", "cgpa"),
    CalculatorEntry("Grade Calculator", "Marks to grade & grade point", "clipboard-check-outline",
                     "grade_calculator", "GPA & Education", "grade"),
    CalculatorEntry("Unit Converter", "Length, weight, temp & more", "swap-horizontal-bold",
                     "unit_converter", "Tools", "unit_converter"),
]


class HomeScreen(MDScreen):
    """Landing screen with a search bar and grouped calculator cards."""

    def on_pre_enter(self, *args):
        self.populate_cards()

    def populate_cards(self, filter_text: str = "") -> None:
        """(Re)build the card list, optionally filtered by search text."""
        container = self.ids.get("card_container")
        if container is None:
            return
        container.clear_widgets()

        filter_text = filter_text.strip().lower()
        entries = [
            entry for entry in CALCULATOR_REGISTRY
            if filter_text in entry.title.lower() or filter_text in entry.category.lower()
        ]

        categories: List[str] = []
        for entry in entries:
            if entry.category not in categories:
                categories.append(entry.category)

        from kivymd.uix.label import MDLabel
        from kivy.metrics import dp

        for category in categories:
            header = MDLabel(
                text=category,
                bold=True,
                font_style="Subtitle1",
                adaptive_height=True,
                padding=(dp(4), dp(12)),
            )
            container.add_widget(header)
            for entry in entries:
                if entry.category != category:
                    continue
                card = CalculatorCard(
                    title_text=entry.title,
                    subtitle_text=entry.subtitle,
                    icon_name=entry.icon,
                    screen_name=entry.screen_name,
                )
                card.bind(on_release=lambda _card, name=entry.screen_name: self.open_calculator(name))
                container.add_widget(card)

    def open_calculator(self, screen_name: str) -> None:
        manager = self.manager
        if manager is None:
            return
        manager.transition.direction = "left"
        manager.current = screen_name

    def on_search_text(self, text: str) -> None:
        self.populate_cards(text)
