"""
ASTRA Mission Overview Dashboard View
Primary workstation overview displaying mission status, active astronaut biometrics,
habitat life support gauges, and dynamic trend curves.
"""
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal
from astra.config import THEME, MISSION_NAME, HABITAT_LOCATION
from astra.ui.widgets.metric_card import MetricCard
from astra.ui.widgets.trend_graph import TrendGraph
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager


class DashboardView(QWidget):
    """Primary operational command dashboard."""

    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()

        # Connect to event bus
        bus.vitals_updated.connect(self.on_vitals_updated)
        bus.environment_updated.connect(self.on_env_updated)
        bus.active_astronaut_changed.connect(self.set_active_astronaut)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Header: Mission & Astronaut Quick Profile
        hdr_frame = QFrame()
        hdr_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_surface']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
                padding: 4px;
            }}
        """)
        hdr_layout = QHBoxLayout(hdr_frame)
        hdr_layout.setContentsMargins(16, 10, 16, 10)

        # Mission info
        m_box = QVBoxLayout()
        self.lbl_mission = QLabel(f"MISSION: {MISSION_NAME.upper()}")
        self.lbl_mission.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        m_box.addWidget(self.lbl_mission)
        self.lbl_location = QLabel(f"HABITAT LOCATION: {HABITAT_LOCATION} | MET: DAY 142 / 780")
        self.lbl_location.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        m_box.addWidget(self.lbl_location)
        hdr_layout.addLayout(m_box)

        hdr_layout.addStretch()

        # Active astronaut selector pill
        ast_box = QVBoxLayout()
        self.lbl_astronaut = QLabel("ACTIVE CREW: DR. ALEX VANCE [AST-01]")
        self.lbl_astronaut.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 12px;")
        ast_box.addWidget(self.lbl_astronaut)
        self.lbl_role = QLabel("ROLE: MISSION COMMANDER • HEALTH STATUS: NOMINAL")
        self.lbl_role.setStyleSheet(f"color: {THEME['status_normal']}; font-size: 10px; font-weight: bold;")
        ast_box.addWidget(self.lbl_role)
        hdr_layout.addLayout(ast_box)

        # Quick action buttons
        btn_cam = QPushButton("CAMERA SCREENING")
        btn_cam.setObjectName("primaryBtn")
        btn_cam.clicked.connect(lambda: self.navigate_requested.emit("NAV_CAMERA"))
        hdr_layout.addWidget(btn_cam)

        btn_haz = QPushButton("SPACE HAZARDS")
        btn_haz.clicked.connect(lambda: self.navigate_requested.emit("NAV_HAZARDS"))
        hdr_layout.addWidget(btn_haz)

        main_layout.addWidget(hdr_frame)

        # Scrollable content area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Section 1: Crew Physiological Biometrics Grid
        sec1_lbl = QLabel("CREW PHYSIOLOGICAL BIOMETRICS (PRIMARY TELEMETRY)")
        sec1_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec1_lbl)

        vitals_grid = QGridLayout()
        vitals_grid.setSpacing(10)

        self.card_hr = MetricCard("Heart Rate", "bpm", 60.0, 100.0)
        self.card_spo2 = MetricCard("Blood Oxygen (SpO2)", "%", 95.0, 100.0)
        self.card_bp = MetricCard("Blood Pressure", "mmHg", 90.0, 125.0)
        self.card_temp = MetricCard("Core Temperature", "°C", 36.3, 37.5)
        self.card_resp = MetricCard("Respiratory Rate", "brpm", 12.0, 20.0)
        self.card_hyd = MetricCard("Hydration Index", "%", 80.0, 100.0)

        vitals_grid.addWidget(self.card_hr, 0, 0)
        vitals_grid.addWidget(self.card_spo2, 0, 1)
        vitals_grid.addWidget(self.card_bp, 0, 2)
        vitals_grid.addWidget(self.card_temp, 1, 0)
        vitals_grid.addWidget(self.card_resp, 1, 1)
        vitals_grid.addWidget(self.card_hyd, 1, 2)
        layout.addLayout(vitals_grid)

        # Section 2: Real-Time Physiological Trend Graphs
        graphs_box = QHBoxLayout()
        graphs_box.setSpacing(12)
        self.graph_hr = TrendGraph("Heart Rate Trend", "bpm", 40.0, 160.0, 60.0, 100.0, color_hex="#00E5FF")
        self.graph_spo2 = TrendGraph("SpO2 Saturation Trend", "%", 80.0, 100.0, 95.0, 100.0, color_hex="#00E676")
        graphs_box.addWidget(self.graph_hr)
        graphs_box.addWidget(self.graph_spo2)
        layout.addLayout(graphs_box)

        # Section 3: Habitat Environmental Life Support (ECLSS) Grid
        sec2_lbl = QLabel("HABITAT ENVIRONMENTAL CONDITIONS (ECLSS TELEMETRY)")
        sec2_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(sec2_lbl)

        env_grid = QGridLayout()
        env_grid.setSpacing(10)

        self.card_o2 = MetricCard("Cabin O2", "%", 20.5, 23.5)
        self.card_co2 = MetricCard("Cabin CO2", "mmHg", 0.0, 3.0)
        self.card_press = MetricCard("Cabin Pressure", "kPa", 98.0, 103.0)
        self.card_rad = MetricCard("Radiation Flux", "µSv/h", 10.0, 50.0)

        env_grid.addWidget(self.card_o2, 0, 0)
        env_grid.addWidget(self.card_co2, 0, 1)
        env_grid.addWidget(self.card_press, 0, 2)
        env_grid.addWidget(self.card_rad, 0, 3)
        layout.addLayout(env_grid)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def set_active_astronaut(self, ast_id: str):
        self.active_astronaut_id = ast_id
        row = db_manager.execute_single("SELECT * FROM astronauts WHERE id = ?", (ast_id,))
        if row:
            self.lbl_astronaut.setText(f"ACTIVE CREW: {row['name'].upper()} [{row['callsign']}]")
            self.lbl_role.setText(f"ROLE: {row['role'].upper()}")

    def on_vitals_updated(self, vitals: Dict[str, Any]):
        if vitals.get("astronaut_id") != self.active_astronaut_id:
            return

        hr = vitals.get("heart_rate")
        spo2 = vitals.get("spo2")
        sys_bp = vitals.get("sys_bp")
        dia_bp = vitals.get("dia_bp")
        temp = vitals.get("temperature")
        resp = vitals.get("respiratory_rate")
        hyd = vitals.get("hydration_index")

        # Status classifications
        hr_status = "CRITICAL" if (hr and (hr >= 140 or hr <= 40)) else ("WARNING" if (hr and (hr >= 120 or hr <= 50)) else "NOMINAL")
        spo2_status = "CRITICAL" if (spo2 and spo2 < 88.0) else ("WARNING" if (spo2 and spo2 < 93.0) else "NOMINAL")
        temp_status = "CRITICAL" if (temp and (temp >= 39.0 or temp <= 35.0)) else ("WARNING" if (temp and (temp >= 38.0 or temp <= 35.8)) else "NOMINAL")
        resp_status = "CRITICAL" if (resp and (resp >= 30 or resp <= 8)) else ("WARNING" if (resp and (resp >= 24 or resp <= 10)) else "NOMINAL")

        self.card_hr.set_value(hr, hr_status)
        self.card_spo2.set_value(spo2, spo2_status)
        self.card_bp.set_value(sys_bp, "NOMINAL" if (sys_bp and 90 <= sys_bp <= 135) else "WARNING")
        self.card_temp.set_value(temp, temp_status)
        self.card_resp.set_value(resp, resp_status)
        self.card_hyd.set_value(hyd, "NOMINAL" if (hyd and hyd >= 80) else "WARNING")

        self.graph_hr.add_point(hr)
        self.graph_spo2.add_point(spo2)

    def on_env_updated(self, env: Dict[str, Any]):
        o2 = env.get("o2_percent")
        co2 = env.get("co2_mmhg")
        press = env.get("cabin_pressure_kpa")
        rad = env.get("radiation_rate_usv_h")

        o2_status = "CRITICAL" if (o2 and o2 < 18.0) else ("WARNING" if (o2 and o2 < 19.5) else "NOMINAL")
        co2_status = "CRITICAL" if (co2 and co2 > 5.5) else ("WARNING" if (co2 and co2 > 3.5) else "NOMINAL")
        press_status = "CRITICAL" if (press and press < 90.0) else ("WARNING" if (press and press < 95.0) else "NOMINAL")
        rad_status = "CRITICAL" if (rad and rad > 300.0) else ("WARNING" if (rad and rad > 100.0) else "NOMINAL")

        self.card_o2.set_value(o2, o2_status)
        self.card_co2.set_value(co2, co2_status)
        self.card_press.set_value(press, press_status)
        self.card_rad.set_value(rad, rad_status)
