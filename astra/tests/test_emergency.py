"""
ASTRA Automated Unit Tests: Emergency System & Protocols
"""
import unittest
from astra.emergency.emergency_manager import emergency_manager
from astra.emergency.protocols import protocol_registry
from astra.database.seed_data import seed_all_data


class TestEmergency(unittest.TestCase):

    def setUp(self):
        seed_all_data()

    def test_protocol_retrieval(self):
        protocols = protocol_registry.get_all_protocols()
        self.assertGreaterEqual(len(protocols), 10)
        hypoxia = protocol_registry.get_protocol_by_id("PROT-01")
        self.assertIsNotNone(hypoxia)
        self.assertIn("Decompression", hypoxia["title"])

    def test_emergency_activation_and_resolution(self):
        incident = emergency_manager.activate_emergency(
            astronaut_id="AST-01",
            protocol_id="PROT-02",
            initial_vitals={"heart_rate": 145.0, "sys_bp": 160.0}
        )
        self.assertEqual(incident["status"], "ACTIVE")
        self.assertEqual(incident["protocol"]["id"], "PROT-02")

        emergency_manager.log_action_step("Administered chewable Aspirin 325 mg.")
        self.assertGreaterEqual(len(emergency_manager.active_incident["actions_taken"]), 1)

        emergency_manager.update_status("RESOLVED", "Patient pain resolved. Telemetry normalized.")
        self.assertIsNone(emergency_manager.active_incident)


if __name__ == "__main__":
    unittest.main()
