"""
ASTRA Medical Reports & Diagnostic Dossiers View
Generates, views, exports, and transmits formal aerospace medical reports to Ground Mission Control.
"""
import os
import subprocess
import sys
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from astra.config import THEME, REPORTS_DIR
from astra.reporting.report_generator import report_generator
from astra.physician.comm_manager import comm_manager
from astra.database.db_manager import db_manager
from astra.core.event_bus import bus


class MedicalReportsView(QWidget):
    """Manages clinical medical records, PDF generation, and ground station uplinks."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()

        bus.active_astronaut_changed.connect(self.set_active_astronaut)
        bus.message_status_changed.connect(lambda _: self.refresh_reports())
        self.refresh_reports()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header & Actions
        hdr = QHBoxLayout()
        t_box = QVBoxLayout()
        title_lbl = QLabel("AEROSPACE MEDICAL DOSSIERS & CLINICAL REPORTS")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        t_box.addWidget(title_lbl)
        sub_lbl = QLabel("Official clinical reports documenting vital sign snapshots, camera screening observations, and emergency logs.")
        sub_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        t_box.addWidget(sub_lbl)
        hdr.addLayout(t_box)

        hdr.addStretch()

        self.btn_gen = QPushButton("GENERATE NEW COMPREHENSIVE DOSSIER")
        self.btn_gen.setObjectName("primaryBtn")
        self.btn_gen.clicked.connect(self._create_new_report)
        hdr.addWidget(self.btn_gen)
        layout.addLayout(hdr)

        # Reports Table
        self.table = QTableWidget(5, 6)
        self.table.setHorizontalHeaderLabels([
            "Report UID", "Timestamp", "Type", "Severity", "Ground Link Status", "Actions"
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

    def set_active_astronaut(self, ast_id: str):
        self.active_astronaut_id = ast_id
        self.refresh_reports()

    def refresh_reports(self):
        rows = db_manager.execute_query(
            "SELECT * FROM medical_reports WHERE astronaut_id = ? ORDER BY id DESC LIMIT 25",
            (self.active_astronaut_id,)
        )
        self.table.setRowCount(len(rows))

        for idx, r in enumerate(rows):
            self.table.setItem(idx, 0, QTableWidgetItem(r["report_uid"]))
            t_short = r["timestamp"].replace("T", " ")[:19]
            self.table.setItem(idx, 1, QTableWidgetItem(t_short))
            self.table.setItem(idx, 2, QTableWidgetItem(r["report_type"]))
            
            sev_item = QTableWidgetItem(r["severity"])
            sev_item.setForeground(Qt.red if r["severity"] == "CRITICAL" else Qt.cyan)
            self.table.setItem(idx, 3, sev_item)

            stat_item = QTableWidgetItem(r["transmission_status"])
            if r["transmission_status"] == "ACKNOWLEDGED":
                stat_item.setForeground(Qt.green)
            elif r["transmission_status"] == "DELIVERED":
                stat_item.setForeground(Qt.yellow)
            self.table.setItem(idx, 4, stat_item)

            # Action button widget
            btn_box = QWidget()
            b_layout = QHBoxLayout(btn_box)
            b_layout.setContentsMargins(2, 2, 2, 2)
            b_layout.setSpacing(6)

            btn_open = QPushButton("OPEN PDF")
            btn_open.setStyleSheet("padding: 2px 8px; font-size: 10px;")
            pdf_file = r.get("pdf_path")
            btn_open.clicked.connect(lambda _, p=pdf_file: self._open_pdf(p))
            b_layout.addWidget(btn_open)

            if r["transmission_status"] in ("DRAFT", "QUEUED"):
                btn_send = QPushButton("TRANSMIT")
                btn_send.setObjectName("primaryBtn")
                btn_send.setStyleSheet("padding: 2px 8px; font-size: 10px;")
                btn_send.clicked.connect(lambda _, rep=r: self._transmit_report(rep))
                b_layout.addWidget(btn_send)

            b_layout.addStretch()
            self.table.setCellWidget(idx, 5, btn_box)

    def _create_new_report(self):
        try:
            # Query latest readings
            vitals = db_manager.execute_single(
                "SELECT * FROM health_readings WHERE astronaut_id = ? ORDER BY id DESC LIMIT 1",
                (self.active_astronaut_id,)
            ) or {}
            env = db_manager.execute_single("SELECT * FROM environmental_readings ORDER BY id DESC LIMIT 1") or {}
            cam = db_manager.execute_single(
                "SELECT * FROM camera_assessments WHERE astronaut_id = ? ORDER BY id DESC LIMIT 1",
                (self.active_astronaut_id,)
            ) or {}

            rep = report_generator.generate_report(
                astronaut_id=self.active_astronaut_id,
                report_type="COMPREHENSIVE_ASSESSMENT",
                severity="ROUTINE",
                vitals=vitals,
                environment=env,
                camera_obs=cam,
                summary="Routine comprehensive spaceflight medical evaluation. All multi-factor physiological indicators nominal."
            )
            self.refresh_reports()
            QMessageBox.information(self, "Dossier Created", f"Medical report successfully compiled:\n{rep['pdf_path']}")
            bus.companion_message_requested.emit("Comprehensive medical dossier generated and signed.", "happy")
        except Exception as e:
            QMessageBox.critical(self, "Report Generation Error", f"Failed to generate report: {e}")

    def _open_pdf(self, path: Optional[str]):
        if not path or not os.path.exists(path):
            # Check txt fallback
            txt_path = str(path).replace(".pdf", ".txt")
            if os.path.exists(txt_path):
                path = txt_path
            else:
                QMessageBox.warning(self, "File Not Found", "Report file does not exist on disk.")
                return

        try:
            if sys.platform == "win32":
                os.startfile(path)
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            QMessageBox.information(self, "Report Path", f"Report located at:\n{path}")

    def _transmit_report(self, report_record: Dict[str, Any]):
        comm_manager.send_message(
            sender=f"CREW-MEDICAL-OFFICER [{self.active_astronaut_id}]",
            recipient="GROUND-MISSION-CONTROL (MCC)",
            subject=f"CLINICAL REPORT: {report_record['report_uid']}",
            body=report_record["summary"],
            message_type="MEDICAL_REPORT",
            priority="URGENT" if report_record["severity"] == "CRITICAL" else "ROUTINE",
            payload=report_record
        )
        self.refresh_reports()
        QMessageBox.information(self, "Report Transmitted", f"Dossier {report_record['report_uid']} queued for ground downlink.")
