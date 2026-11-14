"""
ASTRA Health Risk Assessment View
Transparent rule-based multi-factor clinical risk breakdown interface.
Shows exactly which indicators triggered alerts, data reliability, missing sensors, and required actions.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.health.models import VitalSigns, EnvironmentalMetrics
from astra.health.risk_engine import risk_engine
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager


class RiskAssessmentView(QWidget):
    """Transparent rule-based risk evaluation interface."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self.latest_vitals: Dict[str, Any] = {}
        self.latest_env: Dict[str, Any] = {}
        self._setup_ui()

        # Connect to event bus
        bus.vitals_updated.connect(lambda v: setattr(self, 'latest_vitals', v))
        bus.environment_updated.connect(lambda e: setattr(self, 'latest_env', e))
        bus.active_astronaut_changed.connect(self.set_active_astronaut)
        self.refresh_alerts()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        # Header Title & Evaluate Button
        hdr = QHBoxLayout()
        t_box = QVBoxLayout()
        title_lbl = QLabel("RULE-BASED HEALTH RISK ASSESSMENT ENGINE")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        t_box.addWidget(title_lbl)
        sub_lbl = QLabel("Transparent multi-factor clinical evaluation combining vitals, symptoms, camera observations, and life-support.")
        sub_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        t_box.addWidget(sub_lbl)
        hdr.addLayout(t_box)

        hdr.addStretch()

        self.btn_eval = QPushButton("TRIGGER INSTANT RISK EVALUATION")
        self.btn_eval.setObjectName("primaryBtn")
        self.btn_eval.clicked.connect(self._run_evaluation)
        hdr.addWidget(self.btn_eval)
        main_layout.addLayout(hdr)

        # Active Alerts Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.alerts_container = QWidget()
        self.alerts_layout = QVBoxLayout(self.alerts_container)
        self.alerts_layout.setContentsMargins(0, 0, 0, 0)
        self.alerts_layout.setSpacing(10)

        scroll.setWidget(self.alerts_container)
        main_layout.addWidget(scroll, stretch=3)

        # Historical Alerts Log Table
        hist_title = QLabel("SYSTEM AUDIT RISK ALERTS LOG")
        hist_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        main_layout.addWidget(hist_title)

        self.table_alerts = QTableWidget(5, 5)
        self.table_alerts.setHorizontalHeaderLabels(["Timestamp", "Severity", "Category", "Trigger Summary", "Status"])
        self.table_alerts.horizontalHeader().setStretchLastSection(True)
        self.table_alerts.verticalHeader().setVisible(False)
        self.table_alerts.setFixedHeight(150)
        main_layout.addWidget(self.table_alerts, stretch=2)

    def set_active_astronaut(self, ast_id: str):
        self.active_astronaut_id = ast_id
        self.refresh_alerts()

    def _run_evaluation(self):
        v_obj = VitalSigns(
            astronaut_id=self.active_astronaut_id,
            heart_rate=self.latest_vitals.get("heart_rate", 68.0),
            spo2=self.latest_vitals.get("spo2", 98.5),
            sys_bp=self.latest_vitals.get("sys_bp", 118.0),
            dia_bp=self.latest_vitals.get("dia_bp", 76.0),
            temperature=self.latest_vitals.get("temperature", 36.6),
            respiratory_rate=self.latest_vitals.get("respiratory_rate", 14.0),
            sensor_connected=self.latest_vitals.get("sensor_connected", True)
        )
        e_obj = EnvironmentalMetrics(
            o2_percent=self.latest_env.get("o2_percent", 21.0),
            co2_mmhg=self.latest_env.get("co2_mmhg", 1.8),
            cabin_pressure_kpa=self.latest_env.get("cabin_pressure_kpa", 101.3),
            radiation_rate_usv_h=self.latest_env.get("radiation_rate_usv_h", 25.0)
        )

        # Fetch recent severe symptoms
        symptoms = db_manager.execute_query(
            "SELECT * FROM symptom_reports WHERE astronaut_id = ? ORDER BY id DESC LIMIT 3",
            (self.active_astronaut_id,)
        )

        alerts = risk_engine.evaluate(vitals=v_obj, environment=e_obj, symptoms=symptoms)
        for a in alerts:
            bus.alert_generated.emit(a.to_dict())

        self.refresh_alerts()
        bus.companion_message_requested.emit(
            f"Risk engine evaluated {len(alerts)} active clinical safety indicators.",
            "concerned" if alerts else "happy"
        )

    def refresh_alerts(self):
        # Clear existing dynamic cards
        while self.alerts_layout.count():
            item = self.alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        rows = db_manager.execute_query(
            "SELECT * FROM health_alerts WHERE astronaut_id = ? ORDER BY id DESC LIMIT 15",
            (self.active_astronaut_id,)
        )

        if not rows:
            nominal_card = QFrame()
            nominal_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {THEME['bg_surface']};
                    border: 1px solid {THEME['status_normal']};
                    border-radius: 8px;
                    padding: 16px;
                }}
            """)
            nc_l = QVBoxLayout(nominal_card)
            t = QLabel("ALL MULTI-FACTOR CLINICAL INDICATORS NOMINAL")
            t.setStyleSheet(f"color: {THEME['status_normal']}; font-weight: bold; font-size: 13px;")
            nc_l.addWidget(t)
            d = QLabel("No abnormal physiological, environmental, or neuro-vestibular excursions detected for current crew member.")
            d.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
            nc_l.addWidget(d)
            self.alerts_layout.addWidget(nominal_card)
        else:
            for r in rows[:4]:
                card = self._build_alert_card(r)
                self.alerts_layout.addWidget(card)

        # Update table
        self.table_alerts.setRowCount(len(rows))
        for idx, r in enumerate(rows):
            t_str = r["timestamp"].split("T")[-1][:8] if "T" in r["timestamp"] else r["timestamp"]
            self.table_alerts.setItem(idx, 0, QTableWidgetItem(t_str))
            sev_item = QTableWidgetItem(r["alert_level"])
            sev_item.setForeground(Qt.red if r["alert_level"] == "CRITICAL" else Qt.yellow)
            self.table_alerts.setItem(idx, 1, sev_item)
            self.table_alerts.setItem(idx, 2, QTableWidgetItem(r["category"]))
            self.table_alerts.setItem(idx, 3, QTableWidgetItem(r["triggering_indicators"]))
            self.table_alerts.setItem(idx, 4, QTableWidgetItem("ACKNOWLEDGED" if r["acknowledged"] else "ACTIVE"))

    def _build_alert_card(self, alert_row: Dict[str, Any]) -> QFrame:
        lvl = alert_row["alert_level"]
        stroke = THEME['status_critical'] if lvl == "CRITICAL" else THEME['status_warning']
        bg_alpha = "rgba(255, 23, 68, 0.15)" if lvl == "CRITICAL" else "rgba(255, 179, 0, 0.12)"

        f = QFrame()
        f.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_alpha};
                border: 1px solid {stroke};
                border-left: 5px solid {stroke};
                border-radius: 8px;
                padding: 12px;
            }}
        """)
        l = QVBoxLayout(f)
        l.setSpacing(6)

        hdr = QHBoxLayout()
        t = QLabel(f"[{lvl}] {alert_row['title'].upper()}")
        t.setStyleSheet(f"color: {stroke}; font-weight: bold; font-size: 12px;")
        hdr.addWidget(t)
        hdr.addStretch()

        ts = QLabel(alert_row["timestamp"].split("T")[-1][:8] if "T" in alert_row["timestamp"] else alert_row["timestamp"])
        ts.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 10px;")
        hdr.addWidget(ts)
        l.addLayout(hdr)

        desc = QLabel(f"• <b>Clinical Explanation:</b> {alert_row['description']}")
        desc.setWordWrap(True)
        l.addWidget(desc)

        trig = QLabel(f"• <b>Triggering Readings:</b> {alert_row['triggering_indicators']}")
        trig.setStyleSheet(f"color: {THEME['text_secondary']};")
        trig.setWordWrap(True)
        l.addWidget(trig)

        if alert_row.get("missing_indicators"):
            miss = QLabel(f"• <b>Missing / Unmonitored Biometrics:</b> {alert_row['missing_indicators']}")
            miss.setStyleSheet("color: #FF8A80; font-style: italic;")
            l.addWidget(miss)

        act = QLabel(f"• <b>Mandatory Action:</b> {alert_row['recommended_action']}")
        act.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold;")
        act.setWordWrap(True)
        l.addWidget(act)

        return f
