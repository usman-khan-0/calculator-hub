"""History screen: browse, delete individual entries, or clear all history."""

from __future__ import annotations

from kivy.app import App
from kivymd.uix.screen import MDScreen


class HistoryScreen(MDScreen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self) -> None:
        container = self.ids.get("history_list") if hasattr(self, "ids") else None
        if container is None:
            return
        container.clear_widgets()

        app = App.get_running_app()
        storage = getattr(app, "storage", None)
        if storage is None:
            return

        from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget

        for record in storage.get_history():
            item = ThreeLineAvatarIconListItem(
                text=f"{record.calculator_type}",
                secondary_text=f"{record.expression} = {record.result}",
                tertiary_text=record.created_at,
            )
            delete_icon = IconRightWidget(icon="delete-outline")
            delete_icon.bind(on_release=lambda *_a, entry_id=record.id: self.delete_entry(entry_id))
            item.add_widget(delete_icon)
            container.add_widget(item)

    def delete_entry(self, entry_id: int) -> None:
        app = App.get_running_app()
        storage = getattr(app, "storage", None)
        if storage is not None:
            storage.delete_history_entry(entry_id)
        self.refresh()

    def clear_all(self) -> None:
        app = App.get_running_app()
        storage = getattr(app, "storage", None)
        if storage is not None:
            storage.clear_history()
        self.refresh()
