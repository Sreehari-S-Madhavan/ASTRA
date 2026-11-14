"""
ASTRA Emergency Response Console View (THIRD PRIORITY)
Zero-navigation immediate life-support emergency workstation with interactive first-aid checklists,
telemetry capture, protocol contraindications, and automatic Flight Surgeon escalation.
"""
from typing import Dict, Any, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QScrollArea, QMessageBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from astra.config import THEME
from astra.emergency.emergency_manager import emergency_manager
from astra.emergency.protocols import protocol_registry
from astra.core.event_bus import bus
from astra.core.audit import log_audit


class EmergencyConsoleView(QWidget):
    """Immediate high-priority emergency life-support workflow view."""

    navigate_requested = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self._setup_ui()

        # Connect to event bus
        bus.emergency_activated.connect(self.on_emergency_activated)
        bus.emergency_resolved.connect(self.on_emergency_resolved)
        self.load_active_incident()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(12)

        # Emergency Header
        hdr = QFrame()
        hdr.setStyleSheet("background-color: rgba(183, 28, 28, 0.45); border: 2px solid #FF1744; border-radius: 8px; padding: 10px;")
        h_layout = QHBoxLayout(hdr)
        
        t_box = QVBoxLayout()
        self.lbl_emerg_title = QLabel("EMERGENCY RESPONSE PROTOCOLS • ZERO-NAVIGATION CONSOLE")
        self.lbl_emerg_title.setStyleSheet("color: #FF1744; font-weight: bold; font-size: 14px; letter-spacing: 1px;")
        t_box.addWidget(self.lbl_emerg_title)

        self.lbl_emerg_sub = QLabel("Select an approved emergency scenario below or execute immediate checklist actions.")
        self.lbl_emerg_sub.setStyleSheet("color: #F0F4FC; font-size: 11px;")
        t_box.addWidget(self.lbl_emerg_sub)
        h_layout.addLayout(t_box)

        h_layout.addStretch()

        self.btn_resolve = QPushButton("STABILIZE & RESOLVE EMERGENCY")
        self.btn_resolve.setStyleSheet("background-color: #00E676; color: black; font-weight: bold; padding: 8px 16px;")
        self.btn_resolve.setEnabled(False)
        self.btn_resolve.clicked.connect(self._resolve_emergency)
        h_layout.addWidget(self.btn_resolve)

        main_layout.addWidget(hdr)

        # 1-Click Fast Activation Grid (10 Predefined Aerospace Scenarios)
        self.act_panel = QFrame()
        self.act_panel.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 10px;")
        ap_layout = QVBoxLayout(self.act_panel)
        ap_title = QLabel("ONE-CLICK FAST EMERGENCY ACTIVATION:")
        ap_title.setStyleSheet(f"color: {THEME['text_secondary']}; font-weight: bold; font-size: 10px; letter-spacing: 0.5px;")
        ap_layout.addWidget(ap_title)

        grid = QGridLayout()
        grid.setSpacing(8)

        scenarios = [
            ("PROT-01", "HYPOXIA / DECOMPRESSION"),
            ("PROT-02", "ACUTE CARDIAC EPISODE"),
            ("PROT-03", "LOSS OF CONSCIOUSNESS"),
            ("PROT-04", "TRAUMATIC HEMORRHAGE"),
            ("PROT-05", "ACUTE RADIATION EVENT"),
            ("PROT-06", "TOXIC CONTAMINATION"),
            ("PROT-07", "SEVERE MOTION SICKNESS"),
            ("PROT-08", "ACUTE SANS CRISIS"),
            ("PROT-09", "ACCIDENTAL HYPOTHERMIA"),
            ("PROT-10", "SEVERE DEHYDRATION")
        ]

        for i, (prot_id, label) in enumerate(scenarios):
            btn = QPushButton(f"▲ {label}")
            btn.setObjectName("emergencyBtn")
            btn.setFixedHeight(32)
            btn.clicked.connect(lambda _, pid=prot_id: self._activate_protocol(pid))
            grid.addWidget(btn, i // 5, i % 5)

        ap_layout.addLayout(grid)
        main_layout.addWidget(self.act_panel)

        # Active Protocol Workflow Display (Checklists & Safety)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        self.workflow_container = QWidget()
        self.wf_layout = QVBoxLayout(self.workflow_container)
        self.wf_layout.setContentsMargins(0, 0, 0, 0)
        self.wf_layout.setSpacing(12)

        scroll.setWidget(self.workflow_container)
        main_layout.addWidget(scroll, stretch=3)

    def load_active_incident(self):
        inc = emergency_manager.get_active_incident()
        if inc:
            self.on_emergency_activated(inc)
        else:
            self._render_idle_state()

    def _render_idle_state(self):
        while self.wf_layout.count():
            item = self.wf_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        card = QFrame()
        card.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 20px;")
        l = QVBoxLayout(card)
        t = QLabel("EMERGENCY SYSTEM ON STANDBY • NO ACTIVE CRITICAL INCIDENT")
        t.setStyleSheet(f"color: {THEME['status_normal']}; font-weight: bold; font-size: 13px;")
        l.addWidget(t)
        desc = QLabel(
            "All vital signs and life support loops are routinely monitored. "
            "If an acute physiological or atmospheric anomaly occurs, click any scenario button above to trigger the authorized first-aid checklist immediately."
        )
        desc.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        l.addWidget(desc)
        self.wf_layout.addWidget(card)
        self.btn_resolve.setEnabled(False)

    def _activate_protocol(self, prot_id: str):
        try:
            inc = emergency_manager.activate_emergency(
                astronaut_id=self.active_astronaut_id,
                protocol_id=prot_id
            )
            QMessageBox.critical(self, "Emergency Protocol Activated", f"ACTIVE EMERGENCY: {inc['protocol']['title']}.\nFollow checklist immediately.")
        except Exception as e:
            QMessageBox.critical(self, "Activation Error", f"Failed to activate protocol: {e}")

    def on_emergency_activated(self, incident: Dict[str, Any]):
        prot = incident.get("protocol") or protocol_registry.get_protocol_by_id(incident.get("protocol_id", "PROT-01"))
        self.lbl_emerg_title.setText(f"ACTIVE EMERGENCY PROTOCOL: {prot['title'].upper()}")
        self.btn_resolve.setEnabled(True)

        # Clear and build dynamic checklist
        while self.wf_layout.count():
            item = self.wf_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # 1. Immediate Safety Alert Box
        s_box = QFrame()
        s_box.setStyleSheet("background-color: rgba(255, 23, 68, 0.20); border: 1px solid #FF1744; border-radius: 8px; padding: 12px;")
        sl = QVBoxLayout(s_box)
        st = QLabel(f"IMMEDIATE CREW SAFETY DIRECTIVE: {prot['immediate_safety']}")
        st.setStyleSheet("color: #FFFFFF; font-weight: bold; font-size: 12px;")
        st.setWordWrap(True)
        sl.addWidget(st)
        self.wf_layout.addWidget(s_box)

        # 2. Step-by-Step Clinical Checklist
        c_frame = QFrame()
        c_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 14px;")
        cl = QVBoxLayout(c_frame)
        cl_title = QLabel("MANDATORY CLINICAL FIRST-AID CHECKLIST:")
        cl_title.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 11px;")
        cl.addWidget(cl_title)

        steps = prot["first_aid_steps"].split("\n")
        for step in steps:
            if step.strip():
                cb = QCheckBox(step.strip())
                cb.setStyleSheet("font-size: 11px; padding: 3px 0;")
                cb.toggled.connect(lambda checked, s=step.strip(): self._on_step_checked(checked, s))
                cl.addWidget(cb)
        self.wf_layout.addWidget(c_frame)

        # 3. Actions to Avoid (Contraindications) & Escalation Criteria
        warn_frame = QFrame()
        warn_frame.setStyleSheet("background-color: rgba(255, 179, 0, 0.15); border: 1px solid #FFB300; border-radius: 8px; padding: 12px;")
        wl = QVBoxLayout(warn_frame)
        c_lbl = QLabel(f"<b>CRITICAL CONTRAINDICATIONS:</b> {prot['contraindications']}")
        c_lbl.setStyleSheet("color: #FFD54F; font-size: 11px;")
        c_lbl.setWordWrap(True)
        wl.addWidget(c_lbl)

        e_lbl = QLabel(f"<b>GROUND ESCALATION CRITERIA:</b> {prot['escalation_criteria']}")
        e_lbl.setStyleSheet("color: #FFD54F; font-size: 11px;")
        e_lbl.setWordWrap(True)
        wl.addWidget(e_lbl)
        self.wf_layout.addWidget(warn_frame)

        # 4. Action Buttons (Report Generation & Ground Uplink)
        btn_box = QHBoxLayout()
        btn_report = QPushButton("GENERATE PRIORITY EMERGENCY MEDICAL DOSSIER")
        btn_report.setObjectName("primaryBtn")
        btn_report.clicked.connect(self._generate_emergency_report)
        btn_box.addWidget(btn_report)

        btn_comm = QPushButton("TRANSMIT EMERGENCY ALERT TO FLIGHT SURGEON")
        btn_comm.clicked.connect(self._transmit_emergency_ground)
        btn_box.addWidget(btn_comm)
        self.wf_layout.addLayout(btn_box)

    def _on_step_checked(self, checked: bool, step_text: str):
        if checked:
            emergency_manager.log_action_step(step_text)
            bus.companion_message_requested.emit(f"Intervention logged: {step_text[:40]}...", "thinking")

    def _generate_emergency_report(self):
        from astra.reporting.report_generator import report_generator
        inc = emergency_manager.get_active_incident() or {}
        rep = report_generator.generate_report(
            astronaut_id=self.active_astronaut_id,
            report_type="EMERGENCY_INCIDENT_REPORT",
            severity="CRITICAL",
            incident_id=inc.get("id"),
            summary=f"Emergency activation of {inc.get('protocol', {}).get('title', 'Emergency')}. First-aid interventions underway."
        )
        QMessageBox.information(self, "Dossier Created", f"Emergency Medical Report generated:\n\n{rep['pdf_path']}")

    def _transmit_emergency_ground(self):
        from astra.physician.comm_manager import comm_manager
        inc = emergency_manager.get_active_incident() or {}
        p_title = inc.get("protocol", {}).get("title", "Emergency Protocol")
        comm_manager.send_message(
            sender=f"CREW-CMO [{self.active_astronaut_id}]",
            recipient="FLIGHT-SURGEON-GROUND",
            subject=f"CRITICAL MEDICAL ESCALATION: {p_title}",
            body=f"Emergency protocol {p_title} active onboard MTV-1. Clinical checklist in progress.",
            message_type="EMERGENCY_ALERT",
            priority="EMERGENCY",
            payload=inc
        )
        QMessageBox.information(self, "Emergency Transmitted", "Priority escalation queued and transmitted to Ground Mission Control.")

    def _resolve_emergency(self):
        emergency_manager.update_status("RESOLVED", "All parameters returned to safe baseline. Crew stabilized.")
        QMessageBox.information(self, "Emergency Resolved", "Condition marked as RESOLVED. Incident archived into medical history.")
        self._render_idle_state()

    def on_emergency_resolved(self, incident: Dict[str, Any]):
        self._render_idle_state()
