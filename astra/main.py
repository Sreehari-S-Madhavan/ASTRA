"""
ASTRA: Astronaut Health & Safety Monitoring System
Main Desktop Application Entry Point
"""
import sys
import os

# Ensure package root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    # Configure high-DPI attributes
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    app = QApplication(sys.argv)
    app.setApplicationName("ASTRA")
    app.setOrganizationName("DeepSpaceMedicine")

    # Initialize SQLite Database & populate initial seed data
    from astra.database.db_manager import db_manager
    from astra.database.seed_data import seed_all_data
    from astra.ui.main_window import MainWindow

    db_manager.init_database()
    seed_all_data()

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
