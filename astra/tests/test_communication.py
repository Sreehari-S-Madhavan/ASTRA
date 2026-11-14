"""
ASTRA Automated Unit Tests: Physician Communication, Reports & Simulator
"""
import os
import unittest
from astra.physician.comm_manager import comm_manager
from astra.reporting.report_generator import report_generator
from astra.simulation.mission_simulator import simulator
from astra.database.seed_data import seed_all_data


class TestCommReportsSimulator(unittest.TestCase):

    def setUp(self):
        seed_all_data()

    def test_comm_queue_dispatch(self):
        comm_manager.set_comm_delay(0.1)
        msg = comm_manager.send_message(
            sender="CREW-CMO",
            recipient="MCC-FLIGHT-SURGEON",
            subject="Routine Morning Telemetry Check",
            body="All vitals nominal.",
            priority="ROUTINE"
        )
        self.assertEqual(msg["status"], "QUEUED")
        queue = comm_manager.get_active_queue()
        self.assertGreaterEqual(len(queue), 1)

    def test_medical_report_pdf_generation(self):
        rep = report_generator.generate_report(
            astronaut_id="AST-01",
            report_type="UNIT_TEST_REPORT",
            severity="ROUTINE",
            vitals={"heart_rate": 72.0, "spo2": 98.0},
            summary="Automated integration test report generation."
        )
        self.assertTrue(os.path.exists(rep["pdf_path"]))
        self.assertTrue(rep["report_uid"].startswith("REP-"))

    def test_mission_simulator_scenario_load(self):
        simulator.load_scenario("HYPOXIA")
        self.assertEqual(simulator.current_scenario_key, "HYPOXIA")
        self.assertEqual(simulator.current_vitals["spo2"], 84.0)
        self.assertEqual(simulator.current_env["cabin_pressure_kpa"], 86.0)

        simulator.load_scenario("NOMINAL")
        self.assertEqual(simulator.current_vitals["spo2"], 98.5)


if __name__ == "__main__":
    unittest.main()
