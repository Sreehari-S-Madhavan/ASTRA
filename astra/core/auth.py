"""
ASTRA Authentication & Role-Based Access Control (RBAC)
Provides cryptographic password hashing, role permissions, and active session management.
"""
import hashlib
import os
import hmac
from typing import Optional, Dict, Set


class Role:
    FLIGHT_SURGEON = "FLIGHT_SURGEON"
    CREW_MEDICAL_OFFICER = "CREW_MEDICAL_OFFICER"
    ASTRONAUT = "ASTRONAUT"
    MISSION_CONTROLLER = "MISSION_CONTROLLER"


ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    Role.FLIGHT_SURGEON: {
        "view_telemetry", "view_reports", "create_reports", "sign_reports",
        "activate_emergency", "resolve_emergency", "edit_protocols", "transmit_ground",
        "run_camera_screening", "adjust_simulation", "view_audit_logs"
    },
    Role.CREW_MEDICAL_OFFICER: {
        "view_telemetry", "view_reports", "create_reports", "activate_emergency",
        "resolve_emergency", "transmit_ground", "run_camera_screening", "adjust_simulation"
    },
    Role.ASTRONAUT: {
        "view_telemetry", "log_symptoms", "run_camera_screening", "activate_emergency",
        "view_companion", "view_wellness"
    },
    Role.MISSION_CONTROLLER: {
        "view_telemetry", "view_reports", "transmit_ground", "view_audit_logs"
    }
}


def hash_password(password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
    """Hashes a password using PBKDF2-HMAC-SHA256 with a unique cryptographic salt."""
    if salt is None:
        salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000)
    return hashed.hex(), salt.hex()


def verify_password(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verifies a password against the stored hash and salt."""
    salt = bytes.fromhex(salt_hex)
    computed_hash = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 100_000).hex()
    return hmac.compare_digest(computed_hash, expected_hash_hex)


class SessionManager:
    """Tracks the currently authenticated user on the workstation."""
    
    def __init__(self):
        # Default active session for immediate desktop prototype readiness
        self.current_user = {
            "callsign": "ROSTOVA",
            "name": "Dr. Elena Rostova",
            "role": Role.CREW_MEDICAL_OFFICER,
            "station": "ONBOARD_MEDICAL_WORKSTATION_1"
        }

    def login(self, callsign: str, role: str, name: str):
        self.current_user = {
            "callsign": callsign,
            "name": name,
            "role": role,
            "station": "ONBOARD_MEDICAL_WORKSTATION_1"
        }

    def logout(self):
        self.current_user = None

    def get_user(self) -> Optional[Dict[str, str]]:
        return self.current_user

    def has_permission(self, permission: str) -> bool:
        if not self.current_user:
            return False
        role = self.current_user.get("role", "")
        return permission in ROLE_PERMISSIONS.get(role, set())


session_manager = SessionManager()
