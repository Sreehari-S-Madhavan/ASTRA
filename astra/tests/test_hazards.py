"""
ASTRA Automated Unit Tests: Spaceflight Hazards Engine
"""
import unittest
from astra.health.hazard_engine import hazard_engine


class TestHazards(unittest.TestCase):

    def test_space_radiation_hazard(self):
        env = {"radiation_rate_usv_h": 450.0}
        events = hazard_engine.evaluate_hazards(env_data=env, vitals_data={}, cam_data={})
        rad_events = [e for e in events if e["hazard_category"] == "SPACE_RADIATION"]
        self.assertEqual(len(rad_events), 1)
        self.assertEqual(rad_events[0]["metric_value"], 450.0)

    def test_eclss_environmental_hazard(self):
        env = {"o2_percent": 16.0, "co2_mmhg": 5.8, "cabin_pressure_kpa": 85.0}
        events = hazard_engine.evaluate_hazards(env_data=env, vitals_data={}, cam_data={})
        env_events = [e for e in events if e["hazard_category"] == "HOSTILE_ENVIRONMENT"]
        self.assertEqual(len(env_events), 1)
        self.assertEqual(env_events[0]["severity"], "CRITICAL")

    def test_isolation_fatigue_hazard(self):
        vitals = {"sleep_hours": 3.5, "fatigue_score": 8.0}
        events = hazard_engine.evaluate_hazards(env_data={}, vitals_data=vitals, cam_data={})
        iso_events = [e for e in events if e["hazard_category"] == "ISOLATION_CONFINEMENT"]
        self.assertEqual(len(iso_events), 1)


if __name__ == "__main__":
    unittest.main()
