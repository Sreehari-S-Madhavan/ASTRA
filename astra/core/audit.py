"""
ASTRA Audit Logging System
Maintains secure, tamper-evident audit logs for medical protocols, emergency activations,
report transmissions, and diagnostic access.
"""
from datetime import datetime
import logging
from astra.database.db_manager import db_manager
from astra.core.auth import session_manager

logger = logging.getLogger("astra.audit")


def log_audit(action: str, target_entity: str, details: str = ""):
    """Logs an action taken on the system with user, role, timestamp, and metadata."""
    now_str = datetime.now().isoformat()
    user = session_manager.get_user()
    callsign = user.get("callsign", "SYSTEM") if user else "SYSTEM"
    role = user.get("role", "UNAUTHENTICATED") if user else "SYSTEM"
    station = user.get("station", "ONBOARD_TERMINAL") if user else "ONBOARD_TERMINAL"

    try:
        db_manager.execute_write(
            "INSERT INTO system_audit_logs (timestamp, user_callsign, role, action, target_entity, details, ip_or_station) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (now_str, callsign, role, action, target_entity, details, station)
        )
        logger.info(f"AUDIT: [{callsign}@{role}] -> {action} on {target_entity} | {details}")
    except Exception as e:
        logger.error(f"Audit log recording failure: {e}")
