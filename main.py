"""Application entry point wiring the view layer."""
from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMainWindow

from views import MainWindowView

logging.basicConfig(level=logging.INFO)


class MainWindow(QMainWindow):
    """Main application window hosting the :class:`MainWindowView`."""

    def __init__(self) -> None:
        super().__init__()

        self.view = MainWindowView()
        self.setCentralWidget(self.view)
        self.setWindowTitle("PyDracula - Modern GUI")
        self.setMinimumSize(940, 560)

        self._connect_view_signals()
        self._populate_demo_data()

    # ------------------------------------------------------------------
    # View signal handlers
    # ------------------------------------------------------------------
    def _connect_view_signals(self) -> None:
        self.view.menu_changed.connect(self._on_menu_changed)
        self.view.save_requested.connect(self._on_save_requested)
        self.view.settings_requested.connect(self._on_settings_requested)

    def _on_menu_changed(self, menu: str) -> None:
        logging.info("Menu changed to %s", menu)
        self.view.show_status_message(f"Switched to {menu.title()} page")

    def _on_save_requested(self) -> None:
        logging.info("Save requested")
        self.view.show_success_animation()
        self.view.show_status_message("Save action triggered")

    def _on_settings_requested(self) -> None:
        logging.info("Settings requested")
        self.view.show_message("Settings", "Settings dialog not implemented yet.")

    # ------------------------------------------------------------------
    # Demo data helpers
    # ------------------------------------------------------------------
    def _populate_demo_data(self) -> None:
        demo_rows = [
            {"name": "Navigation Drawer", "category": "Layouts", "status": "Stable"},
            {"name": "Charts", "category": "Visualization", "status": "Beta"},
            {"name": "Dialogs", "category": "Components", "status": "Stable"},
        ]
        self.view.set_table_data(demo_rows)


def main() -> int:
    app = QApplication(sys.argv)

    icon_path = Path(__file__).resolve().parent / "icon.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
