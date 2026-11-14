"""
ASTRA Physician Communication Manager
Simulates deep space light-time delay, store-and-forward message queues, offline buffering,
and Flight Surgeon ground station acknowledgement workflows.
"""
import time
import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Signal
from astra.database.db_manager import db_manager
from astra.core.event_bus import bus
from astra.core.audit import log_audit
from astra.config import DEFAULT_COMM_DELAY_SECONDS


class CommunicationManager(QObject):
    """Manages transmission queues, light-time propagation delays, and status callbacks."""
    
    queue_updated = Signal(list)
    message_delivered = Signal(dict)
    message_acknowledged = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.simulated_delay_seconds = DEFAULT_COMM_DELAY_SECONDS
        self.offline_mode = False
        
        # Dispatch timer for delayed in-flight packets
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._process_queue)
        self._timer.start(1000)

    def set_comm_delay(self, seconds: float):
        self.simulated_delay_seconds = max(0.0, seconds)

    def set_offline_mode(self, offline: bool):
        self.offline_mode = offline
        log_audit("COMM_MODE_CHANGED", "Ground Link", f"Offline Mode: {offline}")

    def send_message(
        self,
        sender: str,
        recipient: str,
        subject: str,
        body: str,
        message_type: str = "MEDICAL_TELEMETRY",
        priority: str = "ROUTINE",
        payload: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Queues a message or priority report for ground transmission."""
        msg_uid = f"MSG-{uuid.uuid4().hex[:8].upper()}"
        now_str = datetime.now().isoformat()
        payload_json = json.dumps(payload or {})

        db_id = db_manager.execute_write(
            "INSERT INTO communication_messages (msg_uid, sender, recipient, timestamp, message_type, priority, subject, body, payload_json, simulated_delay_sec, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'QUEUED')",
            (msg_uid, sender, recipient, now_str, message_type, priority, subject, body, payload_json, self.simulated_delay_seconds)
        )

        msg_record = {
            "id": db_id,
            "msg_uid": msg_uid,
            "sender": sender,
            "recipient": recipient,
            "timestamp": now_str,
            "message_type": message_type,
            "priority": priority,
            "subject": subject,
            "body": body,
            "payload": payload or {},
            "simulated_delay_sec": self.simulated_delay_seconds,
            "status": "QUEUED",
            "enqueued_time": time.time()
        }

        log_audit("MESSAGE_QUEUED", f"{msg_uid} [{priority}]", f"To: {recipient} | Subject: {subject}")
        self.queue_updated.emit(self.get_active_queue())
        return msg_record

    def get_active_queue(self) -> List[Dict[str, Any]]:
        """Fetch all messages from database ordered by timestamp descending."""
        rows = db_manager.execute_query(
            "SELECT * FROM communication_messages ORDER BY id DESC LIMIT 50"
        )
        return rows

    def _process_queue(self):
        """Simulates physical propagation delay: transitions QUEUED -> TRANSMITTING -> DELIVERED -> ACKNOWLEDGED."""
        if self.offline_mode:
            return  # Store-and-forward active; hold all queued packets onboard

        now = time.time()
        # Find queued and transmitting messages
        queued = db_manager.execute_query(
            "SELECT * FROM communication_messages WHERE status IN ('QUEUED', 'TRANSMITTING') ORDER BY id ASC"
        )
        if not queued:
            return

        for row in queued:
            status = row["status"]
            delay = float(row.get("simulated_delay_sec") or self.simulated_delay_seconds)
            msg_id = row["id"]
            created_ts = datetime.fromisoformat(row["timestamp"]).timestamp()
            elapsed = now - created_ts

            if status == "QUEUED":
                db_manager.execute_write(
                    "UPDATE communication_messages SET status = 'TRANSMITTING' WHERE id = ?",
                    (msg_id,)
                )
                bus.message_status_changed.emit({"id": msg_id, "status": "TRANSMITTING"})
            elif status == "TRANSMITTING" and elapsed >= delay:
                # Arrived at ground station
                deliv_str = datetime.now().isoformat()
                db_manager.execute_write(
                    "UPDATE communication_messages SET status = 'DELIVERED', delivered_at = ? WHERE id = ?",
                    (deliv_str, msg_id)
                )
                self.message_delivered.emit(row)
                bus.message_status_changed.emit({"id": msg_id, "status": "DELIVERED"})
                
                # Ground Flight Surgeon auto-acknowledges urgent/emergency reports after brief review
                self._auto_acknowledge_ground(msg_id, row)

        self.queue_updated.emit(self.get_active_queue())

    def _auto_acknowledge_ground(self, msg_id: int, row: Dict[str, Any]):
        """Simulates ground station flight surgeon reading and signing acknowledgement."""
        ack_str = datetime.now().isoformat()
        db_manager.execute_write(
            "UPDATE communication_messages SET status = 'ACKNOWLEDGED', acknowledged_at = ? WHERE id = ?",
            (ack_str, msg_id)
        )
        # Also update any linked medical report
        db_manager.execute_write(
            "UPDATE medical_reports SET transmission_status = 'ACKNOWLEDGED', acknowledged_at = ? "
            "WHERE report_uid = ? OR incident_id = ?",
            (ack_str, row.get("msg_uid"), row.get("id"))
        )
        log_audit("GROUND_ACKNOWLEDGED", f"Message ID #{msg_id}", f"Flight Surgeon confirmed receipt of {row['subject']}")
        self.message_acknowledged.emit(row)
        bus.message_status_changed.emit({"id": msg_id, "status": "ACKNOWLEDGED"})
        bus.companion_message_requested.emit(
            f"Ground Mission Control acknowledged receipt of transmission: {row['subject']}.",
            "happy"
        )


comm_manager = CommunicationManager()
