"""
ASTRA Astronaut Profile & Medical Baselines View
Displays crew dossiers, mission role assignments, individual physiological baseline metrics,
and allows switching active astronaut monitoring context.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QComboBox, QTableWidget, QTableWidgetItem, QTextEdit, QMessageBox
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.database.db_manager import db_manager
from astra.core.event_bus import bus
from astra.core.audit import log_audit


class ProfileView(QWidget):
    """Astronaut profile management and baseline health metric viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()
        self.refresh_profiles()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header & Profile Switcher
        hdr = QHBoxLayout()
        t_box = QVBoxLayout()
        title_lbl = QLabel("CREW MEMBER PROFILE & INDIVIDUAL PHYSIOLOGICAL BASELINES")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        t_box.addWidget(title_lbl)
        sub_lbl = QLabel("Fictional crew records established for operational mission monitoring and threshold comparison.")
        sub_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        t_box.addWidget(sub_lbl)
        hdr.addLayout(t_box)

        hdr.addStretch()

        hdr.addWidget(QLabel("Select Active Crew Member:"))
        self.combo_astronaut = QComboBox()
        self.combo_astronaut.currentIndexChanged.connect(self._on_astronaut_selected)
        hdr.addWidget(self.combo_astronaut)

        layout.addLayout(hdr)

        # Astronaut Detail Dossier Card
        dossier_frame = QFrame()
        dossier_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px;")
        df_layout = QGridLayout(dossier_frame)
        df_layout.setSpacing(10)

        # Labels
        self.lbl_name = QLabel("Name: --")
        self.lbl_name.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 14px;")
        df_layout.addWidget(self.lbl_name, 0, 0)

        self.lbl_callsign = QLabel("Callsign: --")
        self.lbl_callsign.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 12px;")
        df_layout.addWidget(self.lbl_callsign, 0, 1)

        self.lbl_role = QLabel("Role: --")
        self.lbl_role.setStyleSheet(f"color: {THEME['text_secondary']};")
        df_layout.addWidget(self.lbl_role, 1, 0)

        self.lbl_mission = QLabel("Mission: ARES-V Deep Space Exploration")
        self.lbl_mission.setStyleSheet(f"color: {THEME['text_secondary']};")
        df_layout.addWidget(self.lbl_mission, 1, 1)

        layout.addWidget(dossier_frame)

        # Physiological Baselines Table
        base_title = QLabel("CALIBRATED PHYSIOLOGICAL BASELINE MEASUREMENTS")
        base_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        layout.addWidget(base_title)

        self.table_baselines = QTableWidget(6, 3)
        self.table_baselines.setHorizontalHeaderLabels(["Biometric Parameter", "Individual Baseline", "Standard Fleet Range"])
        self.table_baselines.horizontalHeader().setStretchLastSection(True)
        self.table_baselines.verticalHeader().setVisible(False)
        self.table_baselines.setFixedHeight(185)
        layout.addWidget(self.table_baselines)

        # Medical History Summary
        med_title = QLabel("AUTHORIZED CLINICAL SUMMARY & COUNTERMEASURE NOTES")
        med_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        layout.addWidget(med_title)

        self.txt_medical = QTextEdit()
        self.txt_medical.setReadOnly(True)
        self.txt_medical.setFixedHeight(85)
        layout.addWidget(self.txt_medical)

        # Action button
        btn_apply = QPushButton("SET AS ACTIVE CREW MEMBER FOR WORKSTATION")
        btn_apply.setObjectName("primaryBtn")
        btn_apply.clicked.connect(self._apply_active_astronaut)
        layout.addWidget(btn_apply)

        layout.addStretch()

    def refresh_profiles(self):
        rows = db_manager.execute_query("SELECT * FROM astronauts ORDER BY id ASC")
        self.combo_astronaut.blockSignals(True)
        self.combo_astronaut.clear()
        for r in rows:
            self.combo_astronaut.addItem(f"{r['name']} ({r['callsign']})", r["id"])
        self.combo_astronaut.blockSignals(False)
        self._load_astronaut_details(self.active_astronaut_id)

    def _on_astronaut_selected(self, idx: int):
        ast_id = self.combo_astronaut.currentData()
        if ast_id:
            self._load_astronaut_details(ast_id)

    def _load_astronaut_details(self, ast_id: str):
        row = db_manager.execute_single("SELECT * FROM astronauts WHERE id = ?", (ast_id,))
        if not row:
            return

        self.lbl_name.setText(f"Name: {row['name']}")
        self.lbl_callsign.setText(f"Callsign: [{row['callsign']}] | ID: {row['id']}")
        self.lbl_role.setText(f"Role: {row['role']} (Age: {row['age']})")
        self.txt_medical.setText(row.get("medical_summary", "No medical history recorded."))

        # Populate baselines
        baselines = [
            ("Resting Heart Rate", f"{row['baseline_hr']:.1f} bpm", "60 - 100 bpm"),
            ("Blood Oxygen (SpO2)", f"{row['baseline_spo2']:.1f} %", ">= 95 %"),
            ("Systolic Blood Pressure", f"{row['baseline_sys_bp']:.0f} mmHg", "90 - 125 mmHg"),
            ("Diastolic Blood Pressure", f"{row['baseline_dia_bp']:.0f} mmHg", "60 - 80 mmHg"),
            ("Core Body Temperature", f"{row['baseline_temp']:.1f} °C", "36.3 - 37.5 °C"),
            ("Respiratory Rate", f"{row['baseline_resp']:.1f} brpm", "12 - 20 brpm")
        ]

        for i, (p_name, p_base, p_norm) in enumerate(baselines):
            self.table_baselines.setItem(i, 0, QTableWidgetItem(p_name))
            i_b = QTableWidgetItem(p_base)
            i_b.setForeground(Qt.cyan)
            self.table_baselines.setItem(i, 1, i_b)
            self.table_baselines.setItem(i, 2, QTableWidgetItem(p_norm))

    def _apply_active_astronaut(self):
        ast_id = self.combo_astronaut.currentData()
        if ast_id:
            self.active_astronaut_id = ast_id
            bus.active_astronaut_changed.emit(ast_id)
            log_audit("ACTIVE_ASTRONAUT_SWITCHED", ast_id, f"Workstation context updated to {ast_id}")
            QMessageBox.information(self, "Active Crew Updated", f"Workstation active astronaut set to {ast_id}.")
            bus.companion_message_requested.emit(f"Switched active medical monitoring context to crew member {ast_id}.", "happy")
