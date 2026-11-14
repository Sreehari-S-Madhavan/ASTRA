"""
ASTRA Main Medical Workstation Window
Combines sidebar navigation, live alert banners, module stacked widgets,
and the interactive virtual space companion console.
"""
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QStackedWidget,
    QPushButton, QLabel, QFrame, QLineEdit, QStatusBar
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QFont
from astra.config import THEME, APP_NAME, APP_FULL_NAME, APP_VERSION
from astra.ui.theme import GLOBAL_STYLESHEET
from astra.ui.widgets.alert_banner import AlertBanner
from astra.companion.companion_widget import CompanionWidget
from astra.companion.voice_engine import voice_engine
from astra.simulation.mission_simulator import simulator
from astra.core.event_bus import bus

# Import Views
from astra.ui.views.dashboard_view import DashboardView
from astra.ui.views.camera_view import CameraScreeningView
from astra.ui.views.health_view import HealthMonitoringView
from astra.ui.views.hazards_view import HazardsMonitoringView
from astra.ui.views.risk_view import RiskAssessmentView
from astra.ui.views.emergency_view import EmergencyConsoleView
from astra.ui.views.reports_view import MedicalReportsView
from astra.ui.views.comm_view import PhysicianCommView
from astra.ui.views.simulator_view import SimulatorView
from astra.ui.views.profile_view import ProfileView
from astra.ui.views.settings_view import SettingsView


class MainWindow(QMainWindow):
    """Primary ASTRA Spacecraft Medical Workstation Shell."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME} • {APP_FULL_NAME} [v{APP_VERSION}]")
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            self.resize(min(1600, int(available.width() * 0.94)), min(1000, int(available.height() * 0.92)))
            self.setMinimumSize(min(1100, available.width()), min(700, available.height()))
        else:
            self.resize(1340, 840)
        self.setStyleSheet(GLOBAL_STYLESHEET)

        self._setup_ui()
        self._connect_signals()

        # Start background mission simulator
        simulator.start(interval_ms=1000)

    def _setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # 1. Top Emergency / Health Alert Banner
        self.alert_banner = AlertBanner(self)
        root_layout.addWidget(self.alert_banner)

        # 2. Main Workstation Body (Sidebar + View Stack + Companion Drawer)
        body_layout = QHBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        # A. Left Sidebar Navigation
        sidebar = self._build_sidebar()
        body_layout.addWidget(sidebar)

        # B. Central Stacked Content Views
        self.stack = QStackedWidget()
        self.v_dashboard = DashboardView()
        self.v_camera = CameraScreeningView()
        self.v_health = HealthMonitoringView()
        self.v_hazards = HazardsMonitoringView()
        self.v_risk = RiskAssessmentView()
        self.v_emergency = EmergencyConsoleView()
        self.v_reports = MedicalReportsView()
        self.v_comm = PhysicianCommView()
        self.v_simulator = SimulatorView()
        self.v_profile = ProfileView()
        self.v_settings = SettingsView()

        self.stack.addWidget(self.v_dashboard)   # Index 0
        self.stack.addWidget(self.v_camera)      # Index 1
        self.stack.addWidget(self.v_health)      # Index 2
        self.stack.addWidget(self.v_hazards)     # Index 3
        self.stack.addWidget(self.v_risk)        # Index 4
        self.stack.addWidget(self.v_emergency)   # Index 5
        self.stack.addWidget(self.v_reports)     # Index 6
        self.stack.addWidget(self.v_comm)        # Index 7
        self.stack.addWidget(self.v_simulator)   # Index 8
        self.stack.addWidget(self.v_profile)     # Index 9
        self.stack.addWidget(self.v_settings)    # Index 10

        body_layout.addWidget(self.stack, stretch=4)

        # C. Right Drawer: Virtual Companion & Voice Assistant
        right_panel = QFrame()
        right_panel.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_surface']};
                border-left: 1px solid {THEME['border']};
            }}
        """)
        right_panel.setFixedWidth(260)
        rp_layout = QVBoxLayout(right_panel)
        rp_layout.setContentsMargins(10, 12, 10, 12)
        rp_layout.setSpacing(10)

        self.companion = CompanionWidget(self)
        rp_layout.addWidget(self.companion)

        # Natural Language / Voice Command Bar
        voice_lbl = QLabel("VOICE & NATURAL TEXT COMMANDS:")
        voice_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 10px; font-weight: bold;")
        rp_layout.addWidget(voice_lbl)

        self.txt_voice_cmd = QLineEdit()
        self.txt_voice_cmd.setPlaceholderText("Say / type: 'Check health', 'Run screening'...")
        self.txt_voice_cmd.returnPressed.connect(self._handle_voice_input)
        rp_layout.addWidget(self.txt_voice_cmd)

        btn_voice_send = QPushButton("PROCESS COMMAND")
        btn_voice_send.clicked.connect(self._handle_voice_input)
        rp_layout.addWidget(btn_voice_send)

        self.btn_voice_listen = QPushButton("START OFFLINE VOICE COMMAND")
        self.btn_voice_listen.setToolTip("Listen once for a spoken command using this computer's offline speech recognizer.")
        self.btn_voice_listen.clicked.connect(voice_engine.toggle_listening)
        rp_layout.addWidget(self.btn_voice_listen)

        rp_layout.addStretch()
        body_layout.addWidget(right_panel)

        root_layout.addLayout(body_layout)

        # 3. Status Bar
        self.status_bar = QStatusBar()
        self.status_bar.setStyleSheet(f"background-color: {THEME['bg_dark']}; color: {THEME['text_muted']}; border-top: 1px solid {THEME['border']};")
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("ASTRA WORKSTATION ONLINE • MTV-1 DEEP SPACE TELEMETRY SYNCED • STATUS: NOMINAL")

    def _build_sidebar(self) -> QFrame:
        sidebar = QFrame()
        sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_surface']};
                border-right: 1px solid {THEME['border']};
            }}
        """)
        sidebar.setFixedWidth(205)
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 16, 10, 16)
        layout.setSpacing(6)

        # Logo / Header
        logo_lbl = QLabel("ASTRA")
        logo_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-size: 20px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(logo_lbl)
        sub_logo = QLabel("DEEP SPACE HEALTH CONSOLE")
        sub_logo.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 8px; font-weight: bold; margin-bottom: 8px;")
        layout.addWidget(sub_logo)

        # Navigation Buttons
        self.nav_buttons = []
        routes = [
            ("MISSION OVERVIEW", 0, "NAV_DASHBOARD"),
            ("CAMERA SCREENING ★", 1, "NAV_CAMERA"),
            ("HEALTH MONITORING", 2, "NAV_HEALTH"),
            ("SPACE HAZARDS", 3, "NAV_HAZARDS"),
            ("RISK ASSESSMENT", 4, "NAV_RISK"),
            ("EMERGENCY RESPONSE", 5, "NAV_EMERGENCY"),
            ("MEDICAL REPORTS", 6, "NAV_REPORTS"),
            ("GROUND COMMS", 7, "NAV_COMMUNICATION"),
            ("MISSION SIMULATOR", 8, "NAV_SIMULATOR"),
            ("ASTRONAUT PROFILE", 9, "NAV_PROFILE"),
            ("SETTINGS & AUDIT", 10, "NAV_SETTINGS")
        ]

        for title, idx, tag in routes:
            btn = QPushButton(title)
            btn.setFixedHeight(34)
            btn.setStyleSheet(f"""
                QPushButton {{
                    text-align: left;
                    padding-left: 10px;
                    background: transparent;
                    border: none;
                    border-radius: 4px;
                    color: {THEME['text_secondary']};
                    font-size: 11px;
                }}
                QPushButton:hover {{
                    background: {THEME['bg_card']};
                    color: {THEME['accent_cyan']};
                }}
            """)
            if tag == "NAV_CAMERA":
                btn.setStyleSheet(btn.styleSheet() + f"QPushButton {{ color: {THEME['accent_cyan']}; font-weight: bold; }}")
            elif tag == "NAV_EMERGENCY":
                btn.setStyleSheet(btn.styleSheet() + f"QPushButton {{ color: {THEME['status_critical']}; font-weight: bold; }}")

            btn.clicked.connect(lambda _, i=idx: self.navigate_to_index(i))
            layout.addWidget(btn)
            self.nav_buttons.append((btn, idx, tag))

        layout.addStretch()
        return sidebar

    def _connect_signals(self):
        self.alert_banner.emergency_triage_requested.connect(lambda _: self.navigate_to_index(5))
        self.v_dashboard.navigate_requested.connect(self._handle_navigation_intent)
        voice_engine.command_recognized.connect(self._handle_voice_command)
        voice_engine.listening_changed.connect(self._update_voice_listen_button)
        voice_engine.voice_error.connect(self._show_voice_error)

    def navigate_to_index(self, index: int):
        self.stack.setCurrentIndex(index)
        # Highlight active button
        for btn, idx, tag in self.nav_buttons:
            if idx == index:
                btn.setStyleSheet(btn.styleSheet() + f"QPushButton {{ background: {THEME['bg_card']}; color: {THEME['accent_cyan']}; border-left: 3px solid {THEME['accent_cyan']}; }}")
            else:
                pass

    def _handle_navigation_intent(self, intent: str):
        mapping = {
            "NAV_DASHBOARD": 0,
            "NAV_CAMERA": 1,
            "NAV_HEALTH": 2,
            "NAV_HAZARDS": 3,
            "NAV_RISK": 4,
            "NAV_EMERGENCY": 5,
            "NAV_REPORTS": 6,
            "NAV_COMMUNICATION": 7,
            "NAV_SIMULATOR": 8,
            "NAV_PROFILE": 9,
            "NAV_SETTINGS": 10
        }
        if intent in mapping:
            self.navigate_to_index(mapping[intent])

    def _handle_voice_input(self):
        txt = self.txt_voice_cmd.text().strip()
        if txt:
            self.txt_voice_cmd.clear()
            voice_engine.process_command(txt)

    def _handle_voice_command(self, intent: str, response_text: str):
        self.companion.say(response_text)
        if intent.startswith("NAV_"):
            self._handle_navigation_intent(intent)
        elif intent == "ACTION_GEN_REPORT":
            self.navigate_to_index(6)
            self.v_reports._create_new_report()

    def _update_voice_listen_button(self, listening: bool):
        self.btn_voice_listen.setText("LISTENING... CLICK TO STOP" if listening else "START OFFLINE VOICE COMMAND")
        self.btn_voice_listen.setEnabled(True)

    def _show_voice_error(self, message: str):
        self.status_bar.showMessage(f"VOICE ERROR: {message}", 10000)

    def closeEvent(self, event):
        """Clean shutdown of camera and simulation threads."""
        voice_engine.stop_listening()
        simulator.stop()
        self.v_camera.shutdown()
        event.accept()
