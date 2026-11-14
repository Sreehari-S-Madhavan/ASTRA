"""
ASTRA Workstation Settings, Security & Audit View
Handles Role-Based Access Control (RBAC) authentication, audio/voice preferences,
camera hardware settings, database maintenance, and security audit log inspection.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QComboBox, QSlider, QTableWidget, QTableWidgetItem, QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from astra.config import THEME, APP_VERSION
from astra.core.auth import session_manager, Role
from astra.companion.voice_engine import voice_engine
from astra.database.db_manager import db_manager
from astra.core.audit import log_audit


class SettingsView(QWidget):
    """Workstation settings, access control, and audit viewer."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self.refresh_audit_logs()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header Title
        title_lbl = QLabel(f"ASTRA WORKSTATION CONFIGURATION & SECURITY [v{APP_VERSION}]")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # 1. Role-Based Access Control (RBAC) Authentication Card
        rbac_frame = QFrame()
        rbac_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        rf_layout = QVBoxLayout(rbac_frame)
        rf_title = QLabel("ROLE-BASED ACCESS CONTROL (RBAC) OPERATOR SESSION")
        rf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        rf_layout.addWidget(rf_title)

        curr_user = session_manager.get_user() or {}
        self.lbl_user_info = QLabel(f"Current Operator: {curr_user.get('name')} | Role: [{curr_user.get('role')}]")
        self.lbl_user_info.setStyleSheet("color: #00E5FF; font-weight: bold;")
        rf_layout.addWidget(self.lbl_user_info)

        r_row = QHBoxLayout()
        r_row.addWidget(QLabel("Switch Workstation Role:"))
        self.combo_roles = QComboBox()
        self.combo_roles.addItem("Crew Medical Officer (Dr. Elena Rostova)", (Role.CREW_MEDICAL_OFFICER, "Dr. Elena Rostova", "ROSTOVA"))
        self.combo_roles.addItem("Flight Surgeon Ground Lead (Dr. Sarah Okonjo)", (Role.FLIGHT_SURGEON, "Dr. Sarah Okonjo", "MED-LEAD"))
        self.combo_roles.addItem("Mission Commander (Dr. Alex Vance)", (Role.ASTRONAUT, "Dr. Alex Vance", "VANCE"))
        self.combo_roles.addItem("Flight Engineer (Marcus Chen)", (Role.ASTRONAUT, "Marcus Chen", "CHEN"))
        self.combo_roles.addItem("Ground Mission Controller (MCC Console)", (Role.MISSION_CONTROLLER, "Flight Director", "FLIGHT"))
        r_row.addWidget(self.combo_roles, stretch=2)

        btn_switch_role = QPushButton("APPLY OPERATOR ROLE")
        btn_switch_role.setObjectName("primaryBtn")
        btn_switch_role.clicked.connect(self._switch_role)
        r_row.addWidget(btn_switch_role, stretch=1)
        rf_layout.addLayout(r_row)
        layout.addWidget(rbac_frame)

        # 2. Audio & Companion Settings Card
        audio_frame = QFrame()
        audio_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        af_layout = QVBoxLayout(audio_frame)
        af_title = QLabel("VOICE ASSISTANT & AUDIO SYNTHESIS SETTINGS")
        af_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        af_layout.addWidget(af_title)

        a_row = QHBoxLayout()
        self.btn_mute_all = QPushButton("MUTE VOICE ASSISTANT")
        self.btn_mute_all.setCheckable(True)
        self.btn_mute_all.clicked.connect(self._toggle_mute)
        a_row.addWidget(self.btn_mute_all)

        btn_test_speech = QPushButton("TEST VOICE SYNTHESIS")
        btn_test_speech.clicked.connect(lambda: voice_engine.speak("Audio check nominal. Astraea speech synthesis active."))
        a_row.addWidget(btn_test_speech)
        af_layout.addLayout(a_row)
        layout.addWidget(audio_frame)

        # 3. Security Audit Log Table
        sec_title = QLabel("SYSTEM AUDIT TRAIL (IMMUTABLE LOGS)")
        sec_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        layout.addWidget(sec_title)

        self.table_audit = QTableWidget(6, 5)
        self.table_audit.setHorizontalHeaderLabels(["Timestamp", "Operator", "Role", "Action", "Details"])
        self.table_audit.horizontalHeader().setStretchLastSection(True)
        self.table_audit.verticalHeader().setVisible(False)
        self.table_audit.setFixedHeight(180)
        layout.addWidget(self.table_audit)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _switch_role(self):
        role_tuple = self.combo_roles.currentData()
        if role_tuple:
            role, name, callsign = role_tuple
            session_manager.login(callsign, role, name)
            self.lbl_user_info.setText(f"Current Operator: {name} | Role: [{role}]")
            log_audit("USER_LOGIN", callsign, f"Switched operator to {name} [{role}]")
            QMessageBox.information(self, "Operator Updated", f"Workstation permissions updated to {role}.")
            self.refresh_audit_logs()

    def _toggle_mute(self):
        muted = self.btn_mute_all.isChecked()
        voice_engine.set_muted(muted)
        if muted:
            self.btn_mute_all.setText("UNMUTE VOICE ASSISTANT")
            self.btn_mute_all.setStyleSheet(f"background-color: {THEME['status_warning']}; color: black;")
        else:
            self.btn_mute_all.setText("MUTE VOICE ASSISTANT")
            self.btn_mute_all.setStyleSheet("")

    def refresh_audit_logs(self):
        rows = db_manager.execute_query("SELECT * FROM system_audit_logs ORDER BY id DESC LIMIT 20")
        self.table_audit.setRowCount(len(rows))
        for idx, r in enumerate(rows):
            t_str = r["timestamp"].replace("T", " ")[:19]
            self.table_audit.setItem(idx, 0, QTableWidgetItem(t_str))
            self.table_audit.setItem(idx, 1, QTableWidgetItem(r["user_callsign"]))
            self.table_audit.setItem(idx, 2, QTableWidgetItem(r["role"]))
            self.table_audit.setItem(idx, 3, QTableWidgetItem(r["action"]))
            self.table_audit.setItem(idx, 4, QTableWidgetItem(f"{r['target_entity']} | {r.get('details', '')}"))
