"""
ASTRA Automated Unit Tests: Database Operations
"""
import unittest
from astra.database.db_manager import db_manager


class TestDatabase(unittest.TestCase):

    def setUp(self):
        db_manager.init_database()

    def test_schema_initialization(self):
        tables = db_manager.execute_query("SELECT name FROM sqlite_master WHERE type='table'")
        names = [t["name"] for t in tables]
        expected = [
            "missions", "astronauts", "health_readings", "symptom_reports",
            "camera_assessments", "environmental_readings", "hazard_events",
            "health_alerts", "medical_protocols", "emergency_incidents",
            "physician_profiles", "medical_reports", "communication_messages",
            "system_audit_logs"
        ]
        for exp in expected:
            self.assertIn(exp, names, f"Expected table {exp} missing from schema.")

    def test_foreign_key_enforcement(self):
        with self.assertRaises(Exception):
            db_manager.execute_write(
                "INSERT INTO astronauts (id, callsign, name, age, role, mission_id, created_at) "
                "VALUES ('FAIL-01', 'FAIL', 'Dr. Ghost', 30, 'Ghost', 'NON_EXISTENT_MISSION', '2026-01-01')"
            )


if __name__ == "__main__":
    unittest.main()
