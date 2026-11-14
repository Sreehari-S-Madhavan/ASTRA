"""
ASTRA Physiological Health Monitoring & Symptom Logging View
Provides comprehensive physiological parameter tracking, symptom documentation,
historical comparison tables, and trend visualizers.
"""
from typing import Dict, Any, List
from datetime import datetime
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QComboBox, QTextEdit, QDoubleSpinBox,
    QMessageBox, QScrollArea
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.ui.widgets.metric_card import MetricCard
from astra.ui.widgets.trend_graph import TrendGraph
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager
from astra.core.audit import log_audit


class HealthMonitoringView(QWidget):
    """Detailed vital signs monitoring and clinical symptom logger."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()

        # Connect to event bus
        bus.vitals_updated.connect(self.on_vitals_updated)
        bus.active_astronaut_changed.connect(self.set_active_astronaut)
        self.refresh_history()

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

        # 1. Telemetry Cards Grid
        hdr_lbl = QLabel("ASTRONAUT PHYSIOLOGICAL TELEMETRY STREAM")
        hdr_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 12px; letter-spacing: 0.5px;")
        layout.addWidget(hdr_lbl)

        grid = QGridLayout()
        grid.setSpacing(10)

        self.c_hr = MetricCard("Heart Rate", "bpm", 60.0, 100.0)
        self.c_spo2 = MetricCard("Blood Oxygen (SpO2)", "%", 95.0, 100.0)
        self.c_bp = MetricCard("Systolic BP", "mmHg", 90.0, 125.0)
        self.c_temp = MetricCard("Core Body Temp", "°C", 36.3, 37.5)
        self.c_resp = MetricCard("Respiratory Rate", "brpm", 12.0, 20.0)
        self.c_fatigue = MetricCard("Fatigue Score", "/10", 0.0, 5.0)

        grid.addWidget(self.c_hr, 0, 0)
        grid.addWidget(self.c_spo2, 0, 1)
        grid.addWidget(self.c_bp, 0, 2)
        grid.addWidget(self.c_temp, 1, 0)
        grid.addWidget(self.c_resp, 1, 1)
        grid.addWidget(self.c_fatigue, 1, 2)
        layout.addLayout(grid)

        # 2. Historical Trend Charts
        g_box = QHBoxLayout()
        self.g_bp = TrendGraph("Blood Pressure Trend", "mmHg", 70.0, 160.0, 90.0, 125.0, color_hex="#2979FF")
        self.g_temp = TrendGraph("Core Temperature Trend", "°C", 35.0, 40.0, 36.3, 37.5, color_hex="#FFB300")
        g_box.addWidget(self.g_bp)
        g_box.addWidget(self.g_temp)
        layout.addLayout(g_box)

        # 3. Symptom Recording Form & History
        split_box = QHBoxLayout()
        split_box.setSpacing(14)

        # Symptom Entry Card
        sym_frame = QFrame()
        sym_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        sf_layout = QVBoxLayout(sym_frame)
        sf_layout.setSpacing(8)

        sf_title = QLabel("CLINICAL SYMPTOM LOGGING FORM")
        sf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        sf_layout.addWidget(sf_title)

        # Category
        sf_layout.addWidget(QLabel("Symptom System Category:"))
        self.combo_cat = QComboBox()
        self.combo_cat.addItems([
            "Cardiovascular (Chest tightness, Palpitations)",
            "Respiratory (Dyspnea, Cough, Shortness of breath)",
            "Neuro-Vestibular (Vertigo, Motion sickness, Saccades)",
            "Neuro-Ocular (SANS, Blurring, Scotoma, Eye strain)",
            "Musculoskeletal (Back elongation ache, Cramping)",
            "Metabolic / Thermal (Dehydration, Chills, Shivering)",
            "Psychological (Fatigue, Circadian insomnia, Stress)"
        ])
        sf_layout.addWidget(self.combo_cat)

        # Severity
        sf_layout.addWidget(QLabel("Severity Grading:"))
        self.combo_sev = QComboBox()
        self.combo_sev.addItems(["MILD", "MODERATE", "SEVERE"])
        sf_layout.addWidget(self.combo_sev)

        # Description
        sf_layout.addWidget(QLabel("Clinical Description & Context:"))
        self.txt_desc = QTextEdit()
        self.txt_desc.setFixedHeight(65)
        self.txt_desc.setPlaceholderText("Enter specific symptoms, trigger circumstances, or anatomical localization...")
        sf_layout.addWidget(self.txt_desc)

        btn_log_sym = QPushButton("RECORD SYMPTOM IN MEDICAL DOSSIER")
        btn_log_sym.setObjectName("primaryBtn")
        btn_log_sym.clicked.connect(self._log_symptom)
        sf_layout.addWidget(btn_log_sym)

        split_box.addWidget(sym_frame, stretch=1)

        # Historical Readings Table
        hist_frame = QFrame()
        hist_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        hf_layout = QVBoxLayout(hist_frame)
        hf_layout.setSpacing(8)

        hf_title = QLabel("RECENT TELEMETRY DOSSIER HISTORY")
        hf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        hf_layout.addWidget(hf_title)

        self.table_history = QTableWidget(6, 5)
        self.table_history.setHorizontalHeaderLabels(["Timestamp", "HR", "SpO2", "BP", "Temp"])
        self.table_history.horizontalHeader().setStretchLastSection(True)
        self.table_history.verticalHeader().setVisible(False)
        self.table_history.setFixedHeight(180)
        hf_layout.addWidget(self.table_history)

        split_box.addWidget(hist_frame, stretch=1)
        layout.addLayout(split_box)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def set_active_astronaut(self, ast_id: str):
        self.active_astronaut_id = ast_id
        self.refresh_history()

    def on_vitals_updated(self, v: Dict[str, Any]):
        if v.get("astronaut_id") != self.active_astronaut_id:
            return

        hr = v.get("heart_rate")
        spo2 = v.get("spo2")
        sys_bp = v.get("sys_bp")
        temp = v.get("temperature")
        resp = v.get("respiratory_rate")
        fatigue = v.get("fatigue_score")

        self.c_hr.set_value(hr)
        self.c_spo2.set_value(spo2)
        self.c_bp.set_value(sys_bp)
        self.c_temp.set_value(temp)
        self.c_resp.set_value(resp)
        self.c_fatigue.set_value(fatigue, "WARNING" if (fatigue and fatigue >= 7) else "NOMINAL")

        self.g_bp.add_point(sys_bp)
        self.g_temp.add_point(temp)

    def _log_symptom(self):
        desc = self.txt_desc.toPlainText().strip()
        if not desc:
            QMessageBox.warning(self, "Input Error", "Please provide a symptom description before recording.")
            return

        cat = self.combo_cat.currentText().split(" (")[0]
        sev = self.combo_sev.currentText()
        now_str = datetime.now().isoformat()

        try:
            db_manager.execute_write(
                "INSERT INTO symptom_reports (astronaut_id, timestamp, category, severity, description, duration_hours, reported_by) "
                "VALUES (?, ?, ?, ?, ?, 1.0, 'CREW_SELF_REPORT')",
                (self.active_astronaut_id, now_str, cat, sev, desc)
            )
            log_audit("SYMPTOM_LOGGED", f"Astronaut: {self.active_astronaut_id}", f"{sev} {cat}: {desc}")
            self.txt_desc.clear()
            QMessageBox.information(self, "Symptom Recorded", f"Symptom '{cat}' ({sev}) added to astronaut medical record.")
            bus.companion_message_requested.emit(f"Symptom logged: {sev} {cat}. Flight Surgeon informed in telemetry packet.", "concerned" if sev != "MILD" else "thinking")
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Failed to record symptom: {e}")

    def refresh_history(self):
        rows = db_manager.execute_query(
            "SELECT timestamp, heart_rate, spo2, sys_bp, dia_bp, temperature FROM health_readings "
            "WHERE astronaut_id = ? ORDER BY id DESC LIMIT 10",
            (self.active_astronaut_id,)
        )
        self.table_history.setRowCount(len(rows))
        for r_idx, r in enumerate(rows):
            t_short = r["timestamp"].split("T")[-1][:8] if "T" in r["timestamp"] else r["timestamp"]
            self.table_history.setItem(r_idx, 0, QTableWidgetItem(t_short))
            self.table_history.setItem(r_idx, 1, QTableWidgetItem(f"{r['heart_rate']:.0f} bpm" if r['heart_rate'] else "--"))
            self.table_history.setItem(r_idx, 2, QTableWidgetItem(f"{r['spo2']:.1f}%" if r['spo2'] else "--"))
            self.table_history.setItem(r_idx, 3, QTableWidgetItem(f"{r['sys_bp']:.0f}/{r['dia_bp']:.0f}" if r['sys_bp'] else "--"))
            self.table_history.setItem(r_idx, 4, QTableWidgetItem(f"{r['temperature']:.1f}°C" if r['temperature'] else "--"))
