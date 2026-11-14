"""
ASTRA Alert Banner Widget
Prominent workstation header banner displaying live system status and 1-click emergency triage jump.
"""
from typing import Optional, Dict, Any
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt, Signal
from astra.config import THEME
from astra.core.event_bus import bus


class AlertBanner(QFrame):
    """High-visibility mission safety status banner."""

    emergency_triage_requested = Signal(str) # (protocol_id or alert_category)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(48)
        self.current_alert: Optional[Dict[str, Any]] = None
        self._setup_ui()
        self.set_nominal()

        # Connect to event bus
        bus.alert_generated.connect(self.display_alert)
        bus.emergency_activated.connect(self.display_emergency)
        bus.emergency_resolved.connect(lambda _: self.set_nominal())

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(12)

        self.lbl_icon = QLabel("●")
        self.lbl_icon.setStyleSheet(f"color: {THEME['status_normal']}; font-size: 16px;")
        layout.addWidget(self.lbl_icon)

        self.lbl_text = QLabel("ALL HABITAT & BIOMETRIC SYSTEMS MONITORED • NOMINAL STATUS")
        self.lbl_text.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px; letter-spacing: 0.5px;")
        layout.addWidget(self.lbl_text)

        layout.addStretch()

        self.btn_action = QPushButton("VIEW PROTOCOL")
        self.btn_action.setObjectName("emergencyBtn")
        self.btn_action.setFixedHeight(30)
        self.btn_action.setVisible(False)
        self.btn_action.clicked.connect(self._on_action_clicked)
        layout.addWidget(self.btn_action)

    def set_nominal(self):
        self.current_alert = None
        self.lbl_icon.setText("●")
        self.lbl_icon.setStyleSheet(f"color: {THEME['status_normal']}; font-size: 16px;")
        self.lbl_text.setText("ALL HABITAT & BIOMETRIC SYSTEMS MONITORED • NOMINAL STATUS")
        self.btn_action.setVisible(False)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_surface']};
                border-bottom: 2px solid {THEME['status_normal']};
            }}
        """)

    def display_alert(self, alert_dict: Dict[str, Any]):
        self.current_alert = alert_dict
        level = alert_dict.get("alert_level", "WARNING")
        title = alert_dict.get("title", "Clinical Alert")

        if level == "CRITICAL":
            self.lbl_icon.setText("▲")
            self.lbl_icon.setStyleSheet(f"color: {THEME['status_critical']}; font-size: 18px;")
            self.lbl_text.setText(f"CRITICAL HEALTH ALERT: {title.upper()} — IMMEDIATE ATTENTION REQUIRED")
            self.btn_action.setText("ACTIVATE EMERGENCY TRIAGE")
            self.btn_action.setVisible(True)
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(183, 28, 28, 0.45);
                    border-bottom: 2px solid {THEME['status_critical']};
                }}
            """)
        elif level == "MODERATE":
            self.lbl_icon.setText("▲")
            self.lbl_icon.setStyleSheet(f"color: {THEME['status_warning']}; font-size: 18px;")
            self.lbl_text.setText(f"WARNING: {title.upper()} — THRESHOLD EXCURSION DETECTED")
            self.btn_action.setText("REVIEW RISK FACTORS")
            self.btn_action.setVisible(True)
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: rgba(255, 179, 0, 0.20);
                    border-bottom: 2px solid {THEME['status_warning']};
                }}
            """)

    def display_emergency(self, incident: Dict[str, Any]):
        p_title = incident.get("protocol", {}).get("title", incident.get("incident_type", "EMERGENCY"))
        self.lbl_icon.setText("▲")
        self.lbl_icon.setStyleSheet(f"color: {THEME['status_critical']}; font-size: 20px;")
        self.lbl_text.setText(f"ACTIVE EMERGENCY PROTOCOL IN PROGRESS: {p_title.upper()}")
        self.btn_action.setText("OPEN EMERGENCY CONSOLE")
        self.btn_action.setVisible(True)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: rgba(255, 23, 68, 0.40);
                border-bottom: 3px solid {THEME['status_critical']};
            }}
        """)

    def _on_action_clicked(self):
        cat = "EMERGENCY"
        if self.current_alert:
            cat = self.current_alert.get("category", "EMERGENCY")
        self.emergency_triage_requested.emit(cat)
