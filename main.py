"""Calculator Hub -- main application entry point.

Boots the KivyMD app, loads all KV files, registers every screen with
the ScreenManager, and wires up shared services (SQLite storage).
"""

from __future__ import annotations

import os

from kivy.core.window import Window
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from app.components.calculator_button import CalculatorButton
from app.components.calculator_card import CalculatorCard
from app.components.input_field import LabeledInputField
from app.screens.calculator_screen import (
    AverageCalculatorScreen,
    CGPACalculatorScreen,
    CumulativeGPACalculatorScreen,
    GPACalculatorScreen,
    GradeCalculatorScreen,
    PercentageCalculatorScreen,
    ScientificCalculatorScreen,
    SemesterGPACalculatorScreen,
    SimpleCalculatorScreen,
    UnitConverterScreen,
)
from app.screens.history_screen import HistoryScreen
from app.screens.home_screen import HomeScreen
from app.screens.settings_screen import SETTING_THEME_STYLE, SettingsScreen
from app.utils.storage import DEFAULT_DB_NAME, Storage

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KV_DIR = os.path.join(BASE_DIR, "kv")


class CalculatorHubApp(MDApp):
    """Root application class for Calculator Hub."""

    def build(self):
        self.title = "Calculator Hub"
        self.theme_cls.primary_palette = "Indigo"
        self.theme_cls.accent_palette = "Teal"
        self.theme_cls.theme_style = "Light"

        # Local, offline SQLite storage lives in the app's private data
        # directory on Android, or the current working directory locally.
        db_path = os.path.join(self.user_data_dir, DEFAULT_DB_NAME)
        self.storage = Storage(db_path)

        saved_theme = self.storage.get_setting(SETTING_THEME_STYLE)
        if saved_theme in ("Light", "Dark"):
            self.theme_cls.theme_style = saved_theme

        for kv_file in ("home.kv", "calculator.kv", "settings.kv", "history.kv"):
            Builder.load_file(os.path.join(KV_DIR, kv_file))

        manager = ScreenManager()
        manager.add_widget(HomeScreen())
        manager.add_widget(SimpleCalculatorScreen())
        manager.add_widget(ScientificCalculatorScreen())
        manager.add_widget(GPACalculatorScreen())
        manager.add_widget(SemesterGPACalculatorScreen())
        manager.add_widget(CGPACalculatorScreen())
        manager.add_widget(CumulativeGPACalculatorScreen())
        manager.add_widget(PercentageCalculatorScreen())
        manager.add_widget(GradeCalculatorScreen())
        manager.add_widget(AverageCalculatorScreen())
        manager.add_widget(UnitConverterScreen())
        manager.add_widget(SettingsScreen())
        manager.add_widget(HistoryScreen())
        manager.current = "home"
        Window.bind(on_keyboard=self.on_keyboard)
        return manager

    def on_keyboard(self, window, key, *args):
        """Make the Android hardware/gesture back button navigate back
        instead of closing the app, except on the Home screen."""
        if key == 27:  # ESC / Android back button
            if self.root.current != "home":
                self.go_home()
                return True
            return False
        return False

    def on_stop(self):
        if hasattr(self, "storage"):
            self.storage.close()

    # -- navigation helpers used from KV (app.go_home(), etc.) -----------
    def go_home(self) -> None:
        self.root.transition.direction = "right"
        self.root.current = "home"

    def open_settings(self) -> None:
        self.root.transition.direction = "left"
        self.root.current = "settings"

    def open_history(self) -> None:
        self.root.transition.direction = "left"
        self.root.current = "history"


def main() -> None:
    CalculatorHubApp().run()


if __name__ == "__main__":
    main()
