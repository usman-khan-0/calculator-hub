"""Settings screen: theme, decimal precision, default GPA scale, history."""

from __future__ import annotations

from kivy.app import App
from kivy.properties import BooleanProperty, StringProperty
from kivymd.uix.screen import MDScreen

from app.data.grade_scales import available_scales

SETTING_THEME_STYLE = "theme_style"
SETTING_PRECISION = "decimal_precision"
SETTING_DEFAULT_GPA_SCALE = "default_gpa_scale"


class SettingsScreen(MDScreen):
    theme_style = StringProperty("Light")
    precision_text = StringProperty("6")
    default_scale = StringProperty("4.0 Scale")

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        storage = getattr(app, "storage", None)
        if storage is None:
            return
        self.theme_style = storage.get_setting(SETTING_THEME_STYLE, "Light")
        self.precision_text = storage.get_setting(SETTING_PRECISION, "6")
        self.default_scale = storage.get_setting(SETTING_DEFAULT_GPA_SCALE, "4.0 Scale")

    def available_scale_names(self):
        return available_scales()

    def set_theme(self, style: str) -> None:
        self.theme_style = style
        app = App.get_running_app()
        if app is None:
            return
        app.theme_cls.theme_style = style
        if hasattr(app, "storage"):
            app.storage.set_setting(SETTING_THEME_STYLE, style)

    def set_precision(self, precision_text: str) -> None:
        self.precision_text = precision_text
        app = App.get_running_app()
        if app is not None and hasattr(app, "storage"):
            app.storage.set_setting(SETTING_PRECISION, precision_text)

    def set_default_scale(self, scale_name: str) -> None:
        self.default_scale = scale_name
        app = App.get_running_app()
        if app is not None and hasattr(app, "storage"):
            app.storage.set_setting(SETTING_DEFAULT_GPA_SCALE, scale_name)

    def clear_history(self) -> None:
        app = App.get_running_app()
        if app is not None and hasattr(app, "storage"):
            app.storage.clear_history()
