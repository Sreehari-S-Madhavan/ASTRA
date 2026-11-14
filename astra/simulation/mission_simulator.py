"""
ASTRA Mission Simulation Engine
Generates realistic physiological and environmental telemetry with selectable mission scenarios,
noise injection, manual overrides, speed scaling, and automatic hazard triggering.
"""
import random
import time
from typing import Dict, Any, Optional
from datetime import datetime
from PySide6.QtCore import QObject, QTimer, Signal
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager


SCENARIOS = {
    "NOMINAL": {
        "name": "Nominal Spaceflight Operations",
        "description": "All life support loops, cabin atmosphere, and crew vital signs within standard baselines.",
        "target_vitals": {"hr": 68.0, "spo2": 98.5, "sys": 118.0, "dia": 76.0, "temp": 36.6, "resp": 14.0, "hyd": 92.0, "sleep": 7.5, "fatigue": 2.0},
        "target_env": {"o2": 21.0, "co2": 1.8, "press": 101.3, "temp": 22.0, "humidity": 48.0, "rad": 25.0, "status": "NOMINAL"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "ELEVATED_HR": {
        "name": "Acute Tachycardia / Exercise Strain",
        "description": "Astronaut heart rate spikes to 135+ bpm following intense EVA physical exertion or arrhythmia.",
        "target_vitals": {"hr": 136.0, "spo2": 96.0, "sys": 142.0, "dia": 88.0, "temp": 37.4, "resp": 24.0, "hyd": 82.0, "sleep": 6.0, "fatigue": 6.0},
        "target_env": {"o2": 20.8, "co2": 2.2, "press": 101.2, "temp": 23.5, "humidity": 55.0, "rad": 26.0, "status": "NOMINAL"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "HYPOXIA": {
        "name": "Cabin Atmospheric Hypoxia & Pressure Drop",
        "description": "Partial cabin depressurization and falling oxygen partial pressure driving SpO2 below 86%.",
        "target_vitals": {"hr": 115.0, "spo2": 84.0, "sys": 135.0, "dia": 85.0, "temp": 36.5, "resp": 28.0, "hyd": 88.0, "sleep": 7.0, "fatigue": 7.0},
        "target_env": {"o2": 16.5, "co2": 2.5, "press": 86.0, "temp": 18.0, "humidity": 40.0, "rad": 30.0, "status": "CRITICAL_PRESSURE"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "DECOMPRESSION": {
        "name": "Hull Puncture & Rapid Decompression",
        "description": "Micro-meteoroid penetration causing acute atmospheric loss and rapid hypobaric hypoxia.",
        "target_vitals": {"hr": 128.0, "spo2": 81.0, "sys": 140.0, "dia": 90.0, "temp": 35.8, "resp": 30.0, "hyd": 85.0, "sleep": 6.0, "fatigue": 8.0},
        "target_env": {"o2": 15.0, "co2": 2.2, "press": 82.0, "temp": 16.0, "humidity": 35.0, "rad": 32.0, "status": "RAPID_DECOMPRESSION"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "HYPERCAPNIA": {
        "name": "ECLSS CO2 Scrubber Saturation",
        "description": "Amine bed failure causes carbon dioxide to accumulate to 5.2 mmHg, provoking headaches and tachypnea.",
        "target_vitals": {"hr": 95.0, "spo2": 95.0, "sys": 138.0, "dia": 90.0, "temp": 36.8, "resp": 22.0, "hyd": 89.0, "sleep": 5.5, "fatigue": 5.0},
        "target_env": {"o2": 20.4, "co2": 5.4, "press": 100.8, "temp": 23.0, "humidity": 58.0, "rad": 25.0, "status": "ECLSS_DEGRADED"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "RADIATION_STORM": {
        "name": "Solar Particle Event (SPE) Radiation Storm",
        "description": "Solar coronal mass ejection directed at spacecraft; dosimeters detect 350+ µSv/h flux.",
        "target_vitals": {"hr": 92.0, "spo2": 97.5, "sys": 124.0, "dia": 80.0, "temp": 37.1, "resp": 16.0, "hyd": 86.0, "sleep": 6.0, "fatigue": 4.0},
        "target_env": {"o2": 21.0, "co2": 1.9, "press": 101.3, "temp": 22.0, "humidity": 45.0, "rad": 420.0, "status": "RADIATION_ALERT"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "DEHYDRATION": {
        "name": "Severe Dehydration & Thermal Strain",
        "description": "ECLSS water recovery fault combined with thermal regulation failure: core temp 38.6°C, hydration 65%.",
        "target_vitals": {"hr": 125.0, "spo2": 97.0, "sys": 98.0, "dia": 62.0, "temp": 38.7, "resp": 20.0, "hyd": 64.0, "sleep": 4.5, "fatigue": 8.0},
        "target_env": {"o2": 21.0, "co2": 2.0, "press": 101.0, "temp": 28.5, "humidity": 68.0, "rad": 25.0, "status": "THERMAL_HIGH"},
        "sensor_connected": True,
        "comm_delay": 3.0,
        "offline": False
    },
    "SENSOR_DISCONNECT": {
        "name": "Biometric Sensor Lead Disconnection",
        "description": "Astronaut biosensor harness detaches or loses telemetry lock during sleep or movement.",
        "target_vitals": {"hr": 0.0, "spo2": 0.0, "sys": 0.0, "dia": 0.0, "temp": 0.0, "resp": 0.0, "hyd": 90.0, "sleep": 7.0, "fatigue": 2.0},
        "target_env": {"o2": 21.0, "co2": 1.8, "press": 101.3, "temp": 22.0, "humidity": 48.0, "rad": 25.0, "status": "NOMINAL"},
        "sensor_connected": False,
        "comm_delay": 3.0,
        "offline": False
    },
    "COMM_FAILURE": {
        "name": "Solar Conjunction Deep Space Comm Blackout",
        "description": "Spacecraft passes behind celestial body; direct Earth link severed. Full offline autonomy mode.",
        "target_vitals": {"hr": 70.0, "spo2": 98.0, "sys": 118.0, "dia": 76.0, "temp": 36.6, "resp": 14.0, "hyd": 91.0, "sleep": 7.0, "fatigue": 3.0},
        "target_env": {"o2": 21.0, "co2": 1.8, "press": 101.3, "temp": 22.0, "humidity": 48.0, "rad": 25.0, "status": "NOMINAL"},
        "sensor_connected": True,
        "comm_delay": 1200.0,  # 20 min Mars latency
        "offline": True
    }
}


class MissionSimulator(QObject):
    """Generates continuous mission telemetry and drives simulation scenarios."""
    
    tick_generated = Signal(dict, dict)  # (vitals, environment)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self.current_scenario_key = "NOMINAL"
        self.speed_multiplier = 1.0
        self.is_running = False

        # Live current values
        self.current_vitals = {
            "heart_rate": 68.0,
            "spo2": 98.5,
            "sys_bp": 118.0,
            "dia_bp": 76.0,
            "temperature": 36.6,
            "respiratory_rate": 14.0,
            "hydration_index": 92.0,
            "sleep_hours": 7.5,
            "fatigue_score": 2.0,
            "sensor_connected": True
        }
        self.current_env = {
            "o2_percent": 21.0,
            "co2_mmhg": 1.8,
            "cabin_pressure_kpa": 101.3,
            "cabin_temp_c": 22.0,
            "humidity_pct": 48.0,
            "radiation_rate_usv_h": 25.0,
            "comm_delay_seconds": 3.0,
            "offline_mode": False,
            "system_status": "NOMINAL"
        }

        # Timer for telemetry ticks
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._step)
        self._db_save_counter = 0

    def start(self, interval_ms: int = 1000):
        self.is_running = True
        self.timer.start(int(interval_ms / max(0.1, self.speed_multiplier)))

    def stop(self):
        self.is_running = False
        self.timer.stop()

    def set_speed(self, multiplier: float):
        self.speed_multiplier = max(0.2, min(10.0, multiplier))
        if self.is_running:
            self.timer.setInterval(int(1000 / self.speed_multiplier))

    def load_scenario(self, scenario_key: str):
        if scenario_key not in SCENARIOS:
            return
        self.current_scenario_key = scenario_key
        sc = SCENARIOS[scenario_key]
        tv = sc["target_vitals"]
        te = sc["target_env"]

        self.current_vitals.update({
            "heart_rate": tv["hr"],
            "spo2": tv["spo2"],
            "sys_bp": tv["sys"],
            "dia_bp": tv["dia"],
            "temperature": tv["temp"],
            "respiratory_rate": tv["resp"],
            "hydration_index": tv["hyd"],
            "sleep_hours": tv["sleep"],
            "fatigue_score": tv["fatigue"],
            "sensor_connected": sc["sensor_connected"]
        })

        self.current_env.update({
            "o2_percent": te["o2"],
            "co2_mmhg": te["co2"],
            "cabin_pressure_kpa": te["press"],
            "cabin_temp_c": te["temp"],
            "humidity_pct": te["humidity"],
            "radiation_rate_usv_h": te["rad"],
            "system_status": te["status"],
            "comm_delay_seconds": sc["comm_delay"],
            "offline_mode": sc["offline"]
        })

        # Step immediately to trigger reactive checks
        self._step()

    def set_manual_vital(self, key: str, value: float):
        self.current_vitals[key] = value

    def set_manual_env(self, key: str, value: float):
        self.current_env[key] = value

    def _step(self):
        now_str = datetime.now().isoformat()
        
        # Apply slight realistic sensor noise if sensor is connected
        if self.current_vitals.get("sensor_connected", True):
            v_payload = {
                "astronaut_id": self.active_astronaut_id,
                "timestamp": now_str,
                "heart_rate": round(max(30.0, self.current_vitals["heart_rate"] + random.uniform(-0.8, 0.8)), 1),
                "spo2": round(min(100.0, max(60.0, self.current_vitals["spo2"] + random.uniform(-0.2, 0.2))), 1),
                "sys_bp": round(max(50.0, self.current_vitals["sys_bp"] + random.uniform(-0.7, 0.7)), 1),
                "dia_bp": round(max(30.0, self.current_vitals["dia_bp"] + random.uniform(-0.5, 0.5)), 1),
                "temperature": round(max(32.0, self.current_vitals["temperature"] + random.uniform(-0.04, 0.04)), 2),
                "respiratory_rate": round(max(4.0, self.current_vitals["respiratory_rate"] + random.uniform(-0.3, 0.3)), 1),
                "hydration_index": round(max(40.0, min(100.0, self.current_vitals["hydration_index"])), 1),
                "sleep_hours": round(self.current_vitals["sleep_hours"], 1),
                "fatigue_score": round(self.current_vitals["fatigue_score"], 1),
                "source_type": "SIMULATED",
                "validity_status": "VALID",
                "sensor_connected": True
            }
        else:
            v_payload = {
                "astronaut_id": self.active_astronaut_id,
                "timestamp": now_str,
                "heart_rate": None,
                "spo2": None,
                "sys_bp": None,
                "dia_bp": None,
                "temperature": None,
                "respiratory_rate": None,
                "hydration_index": self.current_vitals["hydration_index"],
                "sleep_hours": self.current_vitals["sleep_hours"],
                "fatigue_score": self.current_vitals["fatigue_score"],
                "source_type": "SIMULATED",
                "validity_status": "DEGRADED",
                "sensor_connected": False
            }

        e_payload = {
            "timestamp": now_str,
            "o2_percent": round(max(10.0, self.current_env["o2_percent"] + random.uniform(-0.05, 0.05)), 1),
            "co2_mmhg": round(max(0.0, self.current_env["co2_mmhg"] + random.uniform(-0.03, 0.03)), 2),
            "cabin_pressure_kpa": round(max(50.0, self.current_env["cabin_pressure_kpa"] + random.uniform(-0.1, 0.1)), 1),
            "cabin_temp_c": round(self.current_env["cabin_temp_c"] + random.uniform(-0.05, 0.05), 1),
            "humidity_pct": round(self.current_env["humidity_pct"] + random.uniform(-0.2, 0.2), 1),
            "radiation_rate_usv_h": round(max(1.0, self.current_env["radiation_rate_usv_h"] + random.uniform(-1.0, 1.0)), 1),
            "comm_delay_seconds": self.current_env["comm_delay_seconds"],
            "offline_mode": self.current_env["offline_mode"],
            "system_status": self.current_env["system_status"]
        }

        # Emit Qt signal & EventBus
        self.tick_generated.emit(v_payload, e_payload)
        bus.vitals_updated.emit(v_payload)
        bus.environment_updated.emit(e_payload)

        # Periodically persist to DB (every 10 ticks)
        self._db_save_counter += 1
        if self._db_save_counter >= 10:
            self._db_save_counter = 0
            self._persist_tick(v_payload, e_payload)

    def _persist_tick(self, v: Dict[str, Any], e: Dict[str, Any]):
        try:
            db_manager.execute_write(
                "INSERT INTO health_readings (astronaut_id, timestamp, heart_rate, spo2, sys_bp, dia_bp, temperature, respiratory_rate, hydration_index, sleep_hours, fatigue_score, source_type, validity_status, sensor_connected, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    v["astronaut_id"], v["timestamp"], v["heart_rate"], v["spo2"], v["sys_bp"], v["dia_bp"],
                    v["temperature"], v["respiratory_rate"], v["hydration_index"], v["sleep_hours"],
                    v["fatigue_score"], v["source_type"], v["validity_status"], 1 if v["sensor_connected"] else 0,
                    f"Simulation Scenario: {self.current_scenario_key}"
                )
            )
            db_manager.execute_write(
                "INSERT INTO environmental_readings (timestamp, o2_percent, co2_mmhg, cabin_pressure_kpa, cabin_temp_c, humidity_pct, radiation_rate_usv_h, system_status, notes) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    e["timestamp"], e["o2_percent"], e["co2_mmhg"], e["cabin_pressure_kpa"], e["cabin_temp_c"],
                    e["humidity_pct"], e["radiation_rate_usv_h"], e["system_status"],
                    f"Simulation Scenario: {self.current_scenario_key}"
                )
            )
        except Exception as err:
            print(f"Error persisting simulated telemetry: {err}")


simulator = MissionSimulator()
