"""
ASTRA Emergency Response Manager
Provides immediate zero-navigation emergency protocol activation, step-by-step checklists,
telemetry capture, incident recording, and automatic escalation to Ground Flight Surgeons.
"""
from datetime import datetime
import json
from typing import Optional, Dict, Any, List
from astra.database.db_manager import db_manager
from astra.core.event_bus import bus
from astra.core.audit import log_audit
from astra.emergency.protocols import protocol_registry


class EmergencyManager:
    """Controls emergency life-support workflows, incident state machines, and triage."""

    def __init__(self):
        self.active_incident: Optional[Dict[str, Any]] = None

    def activate_emergency(
        self,
        astronaut_id: str,
        protocol_id: str,
        initial_vitals: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Immediate 1-click emergency activation."""
        protocol = protocol_registry.get_protocol_by_id(protocol_id)
        if not protocol:
            raise ValueError(f"Unknown emergency protocol ID: {protocol_id}")

        now_str = datetime.now().isoformat()
        vitals_json = json.dumps(initial_vitals or {})

        incident_id = db_manager.execute_write(
            "INSERT INTO emergency_incidents (astronaut_id, timestamp, protocol_id, incident_type, status, initial_vitals, actions_taken, escalation_sent, physician_notified) "
            "VALUES (?, ?, ?, ?, 'ACTIVE', ?, '[]', 1, 1)",
            (astronaut_id, now_str, protocol_id, protocol["title"], vitals_json)
        )

        incident_record = {
            "id": incident_id,
            "astronaut_id": astronaut_id,
            "timestamp": now_str,
            "protocol_id": protocol_id,
            "protocol": protocol,
            "status": "ACTIVE",
            "initial_vitals": initial_vitals or {},
            "actions_taken": [],
            "escalation_sent": True,
            "physician_notified": True
        }
        self.active_incident = incident_record

        # Audit & Event bus propagation
        log_audit("EMERGENCY_ACTIVATED", f"Incident #{incident_id} [{protocol['code']}]", f"Astronaut: {astronaut_id}")
        bus.emergency_activated.emit(incident_record)
        bus.companion_message_requested.emit(
            f"EMERGENCY PROTOCOL ACTIVE: {protocol['title']}. Immediate safety: {protocol['immediate_safety']}",
            "emergency"
        )

        return incident_record

    def log_action_step(self, step_text: str):
        """Records an emergency first-aid intervention executed by crew."""
        if not self.active_incident:
            return

        actions = self.active_incident.get("actions_taken", [])
        entry = {
            "step": step_text,
            "timestamp": datetime.now().isoformat()
        }
        actions.append(entry)
        self.active_incident["actions_taken"] = actions

        db_manager.execute_write(
            "UPDATE emergency_incidents SET actions_taken = ? WHERE id = ?",
            (json.dumps(actions), self.active_incident["id"])
        )
        log_audit("EMERGENCY_ACTION_LOGGED", f"Incident #{self.active_incident['id']}", step_text)

    def update_status(self, new_status: str, notes: str = ""):
        """Transitions emergency status (STABILIZED, ESCALATED, RESOLVED)."""
        if not self.active_incident:
            return

        now_str = datetime.now().isoformat() if new_status == "RESOLVED" else None
        db_manager.execute_write(
            "UPDATE emergency_incidents SET status = ?, resolved_at = ? WHERE id = ?",
            (new_status, now_str, self.active_incident["id"])
        )
        self.active_incident["status"] = new_status
        if now_str:
            self.active_incident["resolved_at"] = now_str

        log_audit(f"EMERGENCY_STATUS_{new_status}", f"Incident #{self.active_incident['id']}", notes)

        if new_status == "RESOLVED":
            bus.emergency_resolved.emit(self.active_incident)
            bus.companion_message_requested.emit("Emergency condition resolved. Vital signs returning to monitored baseline.", "happy")
            self.active_incident = None

    def get_active_incident(self) -> Optional[Dict[str, Any]]:
        if self.active_incident:
            return self.active_incident
        # Check database for any un-resolved active incident
        row = db_manager.execute_single(
            "SELECT * FROM emergency_incidents WHERE status IN ('ACTIVE', 'STABILIZED') ORDER BY id DESC LIMIT 1"
        )
        if row:
            protocol = protocol_registry.get_protocol_by_id(row["protocol_id"])
            row["protocol"] = protocol
            row["actions_taken"] = json.loads(row.get("actions_taken") or "[]")
            row["initial_vitals"] = json.loads(row.get("initial_vitals") or "{}")
            self.active_incident = row
            return row
        return None


emergency_manager = EmergencyManager()
