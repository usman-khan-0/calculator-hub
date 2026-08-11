"""Calculator screens.

Each screen class is a thin UI layer: all real computation is delegated
to the pure-Python engines in ``app/calculators``. Screens are
responsible only for reading widget state, calling the engine, and
displaying the result or a friendly error message.
"""

from __future__ import annotations

from typing import List

from kivy.metrics import dp
from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivymd.uix.screen import MDScreen

from app.calculators.average import AverageError, calculate_average
from app.calculators.basic import BasicCalculator
from app.calculators.cgpa import CGPACalculatorState
from app.calculators.gpa import GPACalculatorState
from app.calculators.grade import GradeCalculationError, calculate_grade
from app.calculators.gpa import GPAError
from app.calculators.percentage import (
    PercentageError,
    percentage_change,
    percentage_of,
    reverse_percentage,
    what_percentage,
)
from app.calculators.scientific import ScientificCalculator
from app.calculators.unit_converter import UnitConversionError, categories, convert, units_for
from app.data.grade_scales import available_scales, get_scale
from app.utils.calculations import CalculationError, format_result
from app.utils.validators import (
    ValidationError,
    parse_credit_hours,
    parse_float,
    parse_marks,
    validate_course_name,
    validate_obtained_marks,
)


def _show_error(screen: MDScreen, message: str) -> None:
    """Display a friendly error dialog. Never lets an exception crash the UI."""
    dialog = MDDialog(
        title="Something needs fixing",
        text=message,
        buttons=[MDFlatButton(text="OK", on_release=lambda *_: dialog.dismiss())],
    )
    dialog.open()


def _record_history(screen: MDScreen, calculator_type: str, expression: str, result: str) -> None:
    app = screen.app_ref if hasattr(screen, "app_ref") else None
    try:
        from kivy.app import App

        app = App.get_running_app()
        if app is not None and hasattr(app, "storage"):
            app.storage.add_history(calculator_type, expression, result)
    except Exception:
        # History persistence must never break the calculator itself.
        pass


# ---------------------------------------------------------------------------
# Simple / Basic calculator
# ---------------------------------------------------------------------------

class SimpleCalculatorScreen(MDScreen):
    display_text = StringProperty("0")

    def on_pre_enter(self, *args):
        self.engine = BasicCalculator()
        self.display_text = "0"

    def press_key(self, key: str) -> None:
        if key == "C":
            self.engine.clear()
        elif key == "DEL":
            self.engine.backspace()
        elif key == "+/-":
            self.engine.toggle_sign()
        elif key == "=":
            self._equals()
            return
        else:
            self.engine.append(key)
        self.display_text = self.engine.expression or "0"

    def _equals(self) -> None:
        expression = self.engine.expression
        try:
            result = self.engine.equals()
        except CalculationError as exc:
            _show_error(self, str(exc))
            return
        self.display_text = format_result(result)
        _record_history(self, "Simple Calculator", expression, self.display_text)


# ---------------------------------------------------------------------------
# Scientific calculator
# ---------------------------------------------------------------------------

class ScientificCalculatorScreen(MDScreen):
    display_text = StringProperty("0")
    mode_text = StringProperty("DEG")

    def on_pre_enter(self, *args):
        self.engine = ScientificCalculator(degrees=True)
        self.display_text = "0"
        self.mode_text = "DEG"

    def press_key(self, key: str) -> None:
        handlers = {
            "C": self.engine.clear,
            "AC": self.engine.clear_all,
            "DEL": self.engine.backspace,
            "x²": self.engine.apply_square,
            "x³": self.engine.apply_cube,
            "10^x": self.engine.apply_power_of_ten,
            "e^x": self.engine.apply_exp,
            "MC": self.engine.memory_clear,
        }
        if key == "=":
            self._equals()
            return
        if key == "MODE":
            self.mode_text = "DEG" if self.engine.toggle_mode() else "RAD"
            return
        if key == "M+":
            try:
                value = self.engine.equals(record_history=False) if self.engine.expression else self.engine.ans
            except CalculationError as exc:
                _show_error(self, str(exc))
                return
            self.engine.memory_add(value)
            return
        if key == "M-":
            try:
                value = self.engine.equals(record_history=False) if self.engine.expression else self.engine.ans
            except CalculationError as exc:
                _show_error(self, str(exc))
                return
            self.engine.memory_subtract(value)
            return
        if key == "MR":
            self.engine.expression = format_result(self.engine.memory_recall())
            self.display_text = self.engine.expression
            return
        if key in handlers:
            try:
                handlers[key]()
            except CalculationError as exc:
                _show_error(self, str(exc))
                return
            self.display_text = self.engine.expression or "0"
            return

        self.engine.append(key)
        self.display_text = self.engine.expression or "0"

    def _equals(self) -> None:
        expression = self.engine.expression
        try:
            result = self.engine.equals()
        except CalculationError as exc:
            _show_error(self, str(exc))
            return
        self.display_text = format_result(result)
        _record_history(self, "Scientific Calculator", expression, self.display_text)


# ---------------------------------------------------------------------------
# GPA / Semester GPA calculator
# ---------------------------------------------------------------------------

class GPACalculatorScreen(MDScreen):
    result_text = StringProperty("")
    calculator_label = StringProperty("GPA Calculator")

    def on_pre_enter(self, *args):
        self.state = GPACalculatorState()
        self.result_text = ""
        self._refresh_list()

    def available_grades(self) -> List[str]:
        return self.state.scale.grade_letters()

    def available_scale_names(self) -> List[str]:
        return available_scales()

    def set_scale(self, scale_name: str) -> None:
        try:
            self.state.scale = get_scale(scale_name)
        except KeyError as exc:
            _show_error(self, str(exc))

    def add_course(self, name: str, credit_text: str, grade: str) -> None:
        try:
            course_name = validate_course_name(name)
            credits_ = parse_credit_hours(credit_text)
            if not grade:
                raise ValidationError("Select a grade")
            self.state.add_course(course_name, credits_, grade)
        except (ValidationError, GPAError) as exc:
            _show_error(self, str(exc))
            return
        self._refresh_list()

    def remove_course(self, index: int) -> None:
        self.state.remove_course(index)
        self._refresh_list()

    def _refresh_list(self) -> None:
        container = self.ids.get("course_list") if hasattr(self, "ids") else None
        if container is None:
            return
        container.clear_widgets()
        from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget

        for index, course in enumerate(self.state.courses):
            item = OneLineAvatarIconListItem(
                text=f"{course.name} — {course.credit_hours} cr — {course.grade}"
            )
            remove_icon = IconRightWidget(icon="close")
            remove_icon.bind(on_release=lambda *_a, i=index: self.remove_course(i))
            item.add_widget(remove_icon)
            container.add_widget(item)

    def calculate(self) -> None:
        try:
            result = self.state.calculate()
        except GPAError as exc:
            _show_error(self, str(exc))
            return
        self.result_text = (
            f"Total Credits: {format_result(result.total_credits)}\n"
            f"Total Grade Points: {format_result(result.total_grade_points)}\n"
            f"GPA: {format_result(result.gpa)}"
        )
        _record_history(self, self.calculator_label, f"{len(self.state.courses)} courses",
                         format_result(result.gpa))


class SemesterGPACalculatorScreen(GPACalculatorScreen):
    """Identical engine to GPACalculatorScreen; distinct screen/history label."""

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.calculator_label = "Semester GPA"


# ---------------------------------------------------------------------------
# CGPA / Cumulative GPA calculator
# ---------------------------------------------------------------------------

class CGPACalculatorScreen(MDScreen):
    result_text = StringProperty("")
    calculator_label = StringProperty("CGPA Calculator")

    def on_pre_enter(self, *args):
        self.state = CGPACalculatorState()
        self.result_text = ""
        self._refresh_list()

    def add_semester(self, label: str, gpa_text: str, credit_text: str) -> None:
        try:
            semester_label = validate_course_name(label) if label else f"Semester {len(self.state.semesters) + 1}"
            gpa_value = parse_float(gpa_text, "GPA")
            credits_ = parse_credit_hours(credit_text)
            self.state.add_semester(semester_label, gpa_value, credits_)
        except (ValidationError, GPAError) as exc:
            _show_error(self, str(exc))
            return
        self._refresh_list()

    def remove_semester(self, index: int) -> None:
        self.state.remove_semester(index)
        self._refresh_list()

    def _refresh_list(self) -> None:
        container = self.ids.get("semester_list") if hasattr(self, "ids") else None
        if container is None:
            return
        container.clear_widgets()
        from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget

        for index, semester in enumerate(self.state.semesters):
            item = OneLineAvatarIconListItem(
                text=f"{semester.label} — GPA {semester.gpa} — {semester.credit_hours} cr"
            )
            remove_icon = IconRightWidget(icon="close")
            remove_icon.bind(on_release=lambda *_a, i=index: self.remove_semester(i))
            item.add_widget(remove_icon)
            container.add_widget(item)

    def calculate(self) -> None:
        try:
            result = self.state.calculate()
        except GPAError as exc:
            _show_error(self, str(exc))
            return
        self.result_text = (
            f"Total Credits: {format_result(result.total_credits)}\n"
            f"Total Grade Points: {format_result(result.total_grade_points)}\n"
            f"CGPA: {format_result(result.cgpa)}"
        )
        _record_history(self, self.calculator_label, f"{len(self.state.semesters)} semesters",
                         format_result(result.cgpa))


class CumulativeGPACalculatorScreen(CGPACalculatorScreen):
    """Identical engine to CGPACalculatorScreen; distinct screen/history label."""

    def on_pre_enter(self, *args):
        super().on_pre_enter(*args)
        self.calculator_label = "Cumulative GPA"


# ---------------------------------------------------------------------------
# Percentage calculator
# ---------------------------------------------------------------------------

class PercentageCalculatorScreen(MDScreen):
    result_text = StringProperty("")
    mode = StringProperty("percent_of")

    def set_mode(self, mode: str) -> None:
        self.mode = mode
        self.result_text = ""

    def calculate(self, value_a: str, value_b: str) -> None:
        try:
            a = parse_float(value_a, "First value")
            b = parse_float(value_b, "Second value")
            if self.mode == "percent_of":
                result = percentage_of(a, b)
                text = f"{format_result(a)}% of {format_result(b)} = {format_result(result)}"
            elif self.mode == "what_percent":
                result = what_percentage(a, b)
                text = f"{format_result(a)} is {format_result(result)}% of {format_result(b)}"
            elif self.mode == "change":
                change = percentage_change(a, b)
                direction = "increase" if change.increased else "decrease"
                text = f"{format_result(change.percent_change)}% {direction}"
            elif self.mode == "reverse":
                result = reverse_percentage(a, b)
                text = f"{format_result(a)} is {format_result(b)}% of {format_result(result)}"
            else:
                text = "Unknown calculation mode"
        except PercentageError as exc:
            _show_error(self, str(exc))
            return
        except ValidationError as exc:
            _show_error(self, str(exc))
            return
        self.result_text = text
        _record_history(self, "Percentage Calculator", f"{value_a}, {value_b} ({self.mode})", text)


# ---------------------------------------------------------------------------
# Grade calculator
# ---------------------------------------------------------------------------

class GradeCalculatorScreen(MDScreen):
    result_text = StringProperty("")

    def calculate(self, obtained_text: str, total_text: str) -> None:
        try:
            obtained = parse_marks(obtained_text, "Obtained marks")
            total = parse_marks(total_text, "Total marks")
            validate_obtained_marks(obtained, total)
            result = calculate_grade(obtained, total)
        except (ValidationError, GradeCalculationError) as exc:
            _show_error(self, str(exc))
            return
        self.result_text = (
            f"Percentage: {result.percentage}%\n"
            f"Grade: {result.grade}\n"
            f"Grade Point: {result.grade_point}"
        )
        _record_history(self, "Grade Calculator", f"{obtained_text}/{total_text}", result.grade)


# ---------------------------------------------------------------------------
# Average calculator
# ---------------------------------------------------------------------------

class AverageCalculatorScreen(MDScreen):
    result_text = StringProperty("")

    def on_pre_enter(self, *args):
        self.numbers: List[float] = []
        self.result_text = ""
        self._refresh_list()

    def add_number(self, value_text: str) -> None:
        try:
            value = parse_float(value_text, "Number")
        except ValidationError as exc:
            _show_error(self, str(exc))
            return
        self.numbers.append(value)
        self._refresh_list()

    def remove_number(self, index: int) -> None:
        if 0 <= index < len(self.numbers):
            self.numbers.pop(index)
        self._refresh_list()

    def _refresh_list(self) -> None:
        container = self.ids.get("number_list") if hasattr(self, "ids") else None
        if container is None:
            return
        container.clear_widgets()
        from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget

        for index, number in enumerate(self.numbers):
            item = OneLineAvatarIconListItem(text=format_result(number))
            remove_icon = IconRightWidget(icon="close")
            remove_icon.bind(on_release=lambda *_a, i=index: self.remove_number(i))
            item.add_widget(remove_icon)
            container.add_widget(item)

    def calculate(self) -> None:
        try:
            result = calculate_average(self.numbers)
        except AverageError as exc:
            _show_error(self, str(exc))
            return
        mode_text = ", ".join(format_result(m) for m in result.mode) if result.mode else "None"
        self.result_text = (
            f"Count: {result.count}\n"
            f"Sum: {format_result(result.total)}\n"
            f"Mean: {format_result(result.mean)}\n"
            f"Median: {format_result(result.median)}\n"
            f"Mode: {mode_text}"
        )
        _record_history(self, "Average Calculator", f"{len(self.numbers)} numbers",
                         format_result(result.mean))


# ---------------------------------------------------------------------------
# Unit converter
# ---------------------------------------------------------------------------

class UnitConverterScreen(MDScreen):
    result_text = StringProperty("")
    category = StringProperty("Length")
    from_unit = StringProperty("")
    to_unit = StringProperty("")

    def on_pre_enter(self, *args):
        self.category = "Length"
        self._sync_units()

    def available_categories(self) -> List[str]:
        return categories()

    def set_category(self, category_name: str) -> None:
        self.category = category_name
        self._sync_units()

    def _sync_units(self) -> None:
        unit_list = units_for(self.category)
        if unit_list:
            self.from_unit = unit_list[0]
            self.to_unit = unit_list[1] if len(unit_list) > 1 else unit_list[0]

    def available_units(self) -> List[str]:
        return units_for(self.category)

    def _open_menu(self, caller, items, on_select) -> None:
        from kivymd.uix.menu import MDDropdownMenu

        menu_items = [
            {
                "text": item,
                "viewclass": "OneLineListItem",
                "on_release": lambda x=item: on_select(x, menu),
            }
            for item in items
        ]
        menu = MDDropdownMenu(caller=caller, items=menu_items, width_mult=4)
        menu.open()

    def open_category_menu(self, caller) -> None:
        def select(value, menu):
            self.set_category(value)
            menu.dismiss()

        self._open_menu(caller, self.available_categories(), select)

    def open_from_menu(self, caller) -> None:
        def select(value, menu):
            self.from_unit = value
            menu.dismiss()

        self._open_menu(caller, self.available_units(), select)

    def open_to_menu(self, caller) -> None:
        def select(value, menu):
            self.to_unit = value
            menu.dismiss()

        self._open_menu(caller, self.available_units(), select)

    def convert_value(self, value_text: str) -> None:
        try:
            value = parse_float(value_text, "Value")
            result = convert(self.category, value, self.from_unit, self.to_unit)
        except (ValidationError, UnitConversionError) as exc:
            _show_error(self, str(exc))
            return
        self.result_text = f"{format_result(value)} {self.from_unit} = {format_result(result)} {self.to_unit}"
        _record_history(self, "Unit Converter",
                         f"{value_text} {self.from_unit} -> {self.to_unit}", self.result_text)
