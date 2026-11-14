"""
ASTRA Physician Communication Center View
Simulates Earth-spacecraft deep space communications, ground flight surgeon rosters,
propagation light-time latency, transmission queues, and clinical acknowledgements.
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame,
    QTableWidget, QTableWidgetItem, QLineEdit, QTextEdit, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.physician.comm_manager import comm_manager
from astra.database.db_manager import db_manager
from astra.core.event_bus import bus


class PhysicianCommView(QWidget):
    """Ground-to-spacecraft medical telecommunications center."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()

        # Connect to comm manager signals
        comm_manager.queue_updated.connect(self._on_queue_updated)
        self.refresh_roster()
        self.refresh_queue()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(14)

        # Header Title
        t_box = QVBoxLayout()
        title_lbl = QLabel("GROUND MISSION CONTROL • FLIGHT SURGERY COMMUNICATIONS UPLINK")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        t_box.addWidget(title_lbl)
        sub_lbl = QLabel("Store-and-forward transmission system simulating interplanetary radio propagation delay and ground acknowledgements.")
        sub_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        t_box.addWidget(sub_lbl)
        layout.addLayout(t_box)

        # Split: Flight Surgeon Roster & Message Composer
        split_layout = QHBoxLayout()
        split_layout.setSpacing(14)

        # Flight Surgeon Roster Card
        roster_frame = QFrame()
        roster_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        rf_layout = QVBoxLayout(roster_frame)
        rf_title = QLabel("GROUND FLIGHT SURGERY CONSOLE (MCC-HOUSTON / ESOC)")
        rf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        rf_layout.addWidget(rf_title)

        self.table_physicians = QTableWidget(3, 3)
        self.table_physicians.setHorizontalHeaderLabels(["Flight Surgeon", "Console Station", "Duty Status"])
        self.table_physicians.horizontalHeader().setStretchLastSection(True)
        self.table_physicians.verticalHeader().setVisible(False)
        self.table_physicians.setFixedHeight(120)
        rf_layout.addWidget(self.table_physicians)
        split_layout.addWidget(roster_frame, stretch=1)

        # Message Composer Card
        comp_frame = QFrame()
        comp_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        cf_layout = QVBoxLayout(comp_frame)
        cf_title = QLabel("COMPOSE CLINICAL TRANSMISSION TO GROUND SURGEON")
        cf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        cf_layout.addWidget(cf_title)

        c_row = QHBoxLayout()
        self.combo_recipient = QComboBox()
        c_row.addWidget(self.combo_recipient, stretch=2)

        self.combo_priority = QComboBox()
        self.combo_priority.addItems(["ROUTINE", "URGENT", "EMERGENCY"])
        c_row.addWidget(self.combo_priority, stretch=1)
        cf_layout.addLayout(c_row)

        self.txt_subject = QLineEdit()
        self.txt_subject.setPlaceholderText("Transmission Subject / Clinical Query...")
        cf_layout.addWidget(self.txt_subject)

        self.txt_body = QTextEdit()
        self.txt_body.setFixedHeight(50)
        self.txt_body.setPlaceholderText("Detailed telemetry context, clinical impression, or requested procedure authorization...")
        cf_layout.addWidget(self.txt_body)

        btn_send = QPushButton("ENQUEUE & TRANSMIT VIA DEEP SPACE NETWORK")
        btn_send.setObjectName("primaryBtn")
        btn_send.clicked.connect(self._send_message)
        cf_layout.addWidget(btn_send)

        split_layout.addWidget(comp_frame, stretch=1)
        layout.addLayout(split_layout)

        # Transmission Queue & Message History Table
        q_title = QLabel("DSN TRANSMISSION QUEUE & ACKNOWLEDGEMENT FEED")
        q_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        layout.addWidget(q_title)

        self.table_queue = QTableWidget(6, 6)
        self.table_queue.setHorizontalHeaderLabels([
            "Msg UID", "Timestamp", "Priority", "Subject", "Latency (s)", "Ground Status"
        ])
        self.table_queue.horizontalHeader().setStretchLastSection(True)
        self.table_queue.verticalHeader().setVisible(False)
        layout.addWidget(self.table_queue, stretch=2)

    def refresh_roster(self):
        rows = db_manager.execute_query("SELECT * FROM physician_profiles")
        self.combo_recipient.clear()
        self.table_physicians.setRowCount(len(rows))

        for idx, r in enumerate(rows):
            self.table_physicians.setItem(idx, 0, QTableWidgetItem(f"{r['name']} ({r['callsign']})"))
            self.table_physicians.setItem(idx, 1, QTableWidgetItem(r["ground_station"]))
            stat_item = QTableWidgetItem(r["availability_status"])
            stat_item.setForeground(Qt.green if r["availability_status"] == "ON_DUTY" else Qt.yellow)
            self.table_physicians.setItem(idx, 2, stat_item)
            self.combo_recipient.addItem(f"{r['name']} [{r['callsign']}]")

    def refresh_queue(self):
        rows = comm_manager.get_active_queue()
        self._on_queue_updated(rows)

    def _on_queue_updated(self, rows: List[Dict[str, Any]]):
        self.table_queue.setRowCount(len(rows))
        for idx, r in enumerate(rows):
            self.table_queue.setItem(idx, 0, QTableWidgetItem(r["msg_uid"]))
            t_str = r["timestamp"].replace("T", " ")[:19]
            self.table_queue.setItem(idx, 1, QTableWidgetItem(t_str))

            prio_item = QTableWidgetItem(r["priority"])
            prio_item.setForeground(Qt.red if r["priority"] == "EMERGENCY" else (Qt.yellow if r["priority"] == "URGENT" else Qt.white))
            self.table_queue.setItem(idx, 2, prio_item)

            self.table_queue.setItem(idx, 3, QTableWidgetItem(r["subject"]))
            self.table_queue.setItem(idx, 4, QTableWidgetItem(f"{r.get('simulated_delay_sec', 3.0):.1f}s"))

            stat_item = QTableWidgetItem(r["status"])
            if r["status"] == "ACKNOWLEDGED":
                stat_item.setForeground(Qt.green)
            elif r["status"] == "DELIVERED":
                stat_item.setForeground(Qt.cyan)
            elif r["status"] == "TRANSMITTING":
                stat_item.setForeground(Qt.yellow)
            self.table_queue.setItem(idx, 5, stat_item)

    def _send_message(self):
        subj = self.txt_subject.text().strip()
        body = self.txt_body.toPlainText().strip()
        if not subj or not body:
            QMessageBox.warning(self, "Incomplete Message", "Please provide both a subject and body text.")
            return

        recip = self.combo_recipient.currentText()
        prio = self.combo_priority.currentText()

        comm_manager.send_message(
            sender=f"CREW-CMO [{self.active_astronaut_id}]",
            recipient=recip,
            subject=subj,
            body=body,
            priority=prio
        )
        self.txt_subject.clear()
        self.txt_body.clear()
        QMessageBox.information(self, "Transmission Dispatched", "Clinical transmission enqueued for Deep Space Network propagation.")
        bus.companion_message_requested.emit(f"DSN telemetry packet enqueued for ground station. Propagation delay in progress.", "thinking")
