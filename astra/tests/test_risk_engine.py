"""
ASTRA Automated Unit Tests: Rule-Based Health Risk Assessment Engine
"""
import unittest
from astra.health.models import VitalSigns, EnvironmentalMetrics
from astra.health.risk_engine import risk_engine
from astra.database.seed_data import seed_all_data


class TestRiskEngine(unittest.TestCase):

    def setUp(self):
        seed_all_data()

    def test_nominal_evaluation(self):
        v = VitalSigns(astronaut_id="AST-01", heart_rate=72.0, spo2=98.5, sys_bp=118.0, dia_bp=76.0, temperature=36.6)
        e = EnvironmentalMetrics(o2_percent=21.0, co2_mmhg=1.8, cabin_pressure_kpa=101.3, radiation_rate_usv_h=25.0)
        alerts = risk_engine.evaluate(vitals=v, environment=e)
        crit_alerts = [a for a in alerts if a.alert_level == "CRITICAL"]
        self.assertEqual(len(crit_alerts), 0)

    def test_critical_hypoxia_detection(self):
        v = VitalSigns(astronaut_id="AST-01", heart_rate=110.0, spo2=82.0)
        e = EnvironmentalMetrics(o2_percent=17.5, cabin_pressure_kpa=88.0)
        alerts = risk_engine.evaluate(vitals=v, environment=e)
        crit_alerts = [a for a in alerts if a.alert_level == "CRITICAL"]
        self.assertGreaterEqual(len(crit_alerts), 1)
        self.assertTrue(any("Hypoxia" in a.title or "Decompression" in a.title for a in crit_alerts))

    def test_tachycardia_cardiovascular_detection(self):
        v = VitalSigns(astronaut_id="AST-01", heart_rate=148.0, spo2=97.0)
        alerts = risk_engine.evaluate(vitals=v)
        self.assertTrue(any(a.category == "Cardiovascular" for a in alerts))

    def test_sensor_disconnection(self):
        v = VitalSigns(astronaut_id="AST-01", sensor_connected=False)
        alerts = risk_engine.evaluate(vitals=v)
        self.assertTrue(any(a.category == "Sensor Integrity" for a in alerts))


if __name__ == "__main__":
    unittest.main()
