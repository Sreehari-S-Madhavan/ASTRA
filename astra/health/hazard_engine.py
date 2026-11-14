"""
ASTRA Spaceflight Hazard Monitoring Engine
Monitors the five primary human spaceflight hazards identified in aerospace medicine:
1. Space Radiation (SPE / GCR cumulative exposure)
2. Isolation & Confinement (circadian disruption, fatigue, psychological stress)
3. Distance from Earth (light-time comms delay, store-and-forward, autonomous ops)
4. Gravity Fields (microgravity vestibular adaptation, muscular deconditioning, SANS)
5. Hostile & Closed Environments (ECLSS atmosphere, toxic trace gases, pressure integrity)
"""
from typing import Dict, Any, List
from datetime import datetime
from astra.database.db_manager import db_manager


class HazardEngine:
    """Evaluates mission telemetry against the five spaceflight hazard categories."""

    def evaluate_hazards(
        self,
        env_data: Dict[str, Any],
        vitals_data: Dict[str, Any],
        cam_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        events = []
        now_str = datetime.now().isoformat()

        # 1. Space Radiation Hazard
        rad_rate = env_data.get("radiation_rate_usv_h", 25.0)
        if rad_rate > 100.0:
            events.append({
                "hazard_category": "SPACE_RADIATION",
                "severity": "CRITICAL" if rad_rate > 500.0 else "WARNING",
                "metric_name": "Ambient Radiation Rate",
                "metric_value": rad_rate,
                "threshold_breached": f"{rad_rate:.1f} µSv/h > 100.0 µSv/h",
                "mitigation_action": "Crew directed to Water-Shielded Storm Shelter. Seal habitat rad-doors. Log dosimeter totals.",
                "timestamp": now_str
            })

        # 2. Isolation & Confinement
        sleep_hours = vitals_data.get("sleep_hours", 7.5)
        fatigue_score = vitals_data.get("fatigue_score", 2.0)
        if sleep_hours < 5.0 or fatigue_score >= 7.0:
            events.append({
                "hazard_category": "ISOLATION_CONFINEMENT",
                "severity": "WARNING",
                "metric_name": "Circadian Fatigue & Sleep Debt",
                "metric_value": fatigue_score,
                "threshold_breached": f"Sleep: {sleep_hours:.1f}h (<5.0h) | Fatigue: {fatigue_score:.0f}/10 (>=7)",
                "mitigation_action": "Adjust circadian lighting cycle to blue-depleted mode. Schedule 8-hour protected sleep block. Offer companion relaxation protocol.",
                "timestamp": now_str
            })

        # 3. Distance from Earth (Latency / Autonomy)
        comm_latency = env_data.get("comm_delay_seconds", 3.0)
        is_offline = env_data.get("offline_mode", False)
        if is_offline or comm_latency > 600.0:  # > 10 mins (Mars transit)
            events.append({
                "hazard_category": "DISTANCE_FROM_EARTH",
                "severity": "INFO" if not is_offline else "WARNING",
                "metric_name": "Deep Space Telemetry Delay",
                "metric_value": comm_latency,
                "threshold_breached": f"Comm Latency: {comm_latency:.0f}s ({comm_latency/60:.1f} min) | Offline: {is_offline}",
                "mitigation_action": "Store-and-forward queue active. Station operating in autonomous medical diagnostic triage mode.",
                "timestamp": now_str
            })

        # 4. Gravity Fields / Neuro-Vestibular Adaptation
        tracking_err = cam_data.get("tracking_error_px", 0.0)
        reaction_time = cam_data.get("reaction_time_ms", 250.0)
        if tracking_err > 40.0 or reaction_time > 420.0:
            events.append({
                "hazard_category": "GRAVITY_FIELDS",
                "severity": "WARNING",
                "metric_name": "Vestibular Saccadic Incoordination",
                "metric_value": tracking_err,
                "threshold_breached": f"Smooth pursuit error {tracking_err:.1f}px (>40px) | Latency {reaction_time:.0f}ms",
                "mitigation_action": "Avoid abrupt head movements. Perform calibrated 15-minute vestibular recalibration drills. Restrict safety-critical manual maneuvers.",
                "timestamp": now_str
            })

        # 5. Hostile & Closed Environments (ECLSS)
        o2_pct = env_data.get("o2_percent", 21.0)
        co2_val = env_data.get("co2_mmhg", 1.8)
        press_kpa = env_data.get("cabin_pressure_kpa", 101.3)
        if o2_pct < 19.5 or co2_val > 3.5 or press_kpa < 95.0:
            severity = "CRITICAL" if (o2_pct < 18.0 or press_kpa < 88.0 or co2_val > 6.0) else "WARNING"
            events.append({
                "hazard_category": "HOSTILE_ENVIRONMENT",
                "severity": severity,
                "metric_name": "Life Support Atmosphere Anomaly",
                "metric_value": press_kpa,
                "threshold_breached": f"O2: {o2_pct:.1f}% | CO2: {co2_val:.1f} mmHg | Pressure: {press_kpa:.1f} kPa",
                "mitigation_action": "Verify ECLSS manifold loops. Check O2 generation assembly & amine CO2 scrubbers. Prepare emergency breathing masks if values decline.",
                "timestamp": now_str
            })

        # Persist hazard events
        self._record_events(events)
        return events

    def _record_events(self, events: List[Dict[str, Any]]):
        for e in events:
            try:
                db_manager.execute_write(
                    "INSERT INTO hazard_events (timestamp, hazard_category, severity, metric_name, metric_value, threshold_breached, mitigation_action, resolved) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, 0)",
                    (
                        e["timestamp"],
                        e["hazard_category"],
                        e["severity"],
                        e["metric_name"],
                        float(e["metric_value"]),
                        e["threshold_breached"],
                        e["mitigation_action"]
                    )
                )
            except Exception as err:
                print(f"Failed to record hazard event: {err}")


hazard_engine = HazardEngine()
