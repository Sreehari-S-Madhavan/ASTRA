"""
ASTRA Rule-Based Transparent Health Risk Assessment Engine
Combines physiological telemetry, symptoms, environmental factors, and camera observations
into clear, auditable risk evaluations with multi-indicator trigger breakdowns.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from astra.health.models import VitalSigns, EnvironmentalMetrics, CameraObservation, HealthAlert
from astra.config import VITALS_THRESHOLDS, ENVIRONMENT_THRESHOLDS
from astra.database.db_manager import db_manager


class RiskEngine:
    """Evaluates multi-source telemetry against clinical aerospace safety boundaries."""

    def evaluate(
        self,
        vitals: VitalSigns,
        environment: Optional[EnvironmentalMetrics] = None,
        camera_obs: Optional[CameraObservation] = None,
        symptoms: Optional[List[Dict[str, Any]]] = None
    ) -> List[HealthAlert]:
        alerts: List[HealthAlert] = []
        ast_id = vitals.astronaut_id

        # 0. Check Sensor Connectivity & Data Validity
        if not vitals.sensor_connected:
            alerts.append(HealthAlert(
                astronaut_id=ast_id,
                alert_level="MODERATE",
                category="Sensor Integrity",
                title="Physiological Sensor Disconnection",
                description="Telemetry feed indicates primary vital sensor is disconnected or lost contact.",
                triggering_indicators=["sensor_connected == False"],
                missing_indicators=["Real-time continuous biometric stream"],
                recommended_action="Verify biosensor lead attachment, recharge wearable pack, or switch to manual input."
            ))
            return alerts

        # 1. Critical Hypoxia & Cabin Atmosphere Analysis
        hypoxia_triggers = []
        if vitals.spo2 is not None and vitals.spo2 < VITALS_THRESHOLDS["spo2"]["crit_low"]:
            hypoxia_triggers.append(f"Severe Hypoxemia: SpO2 {vitals.spo2:.1f}% (< {VITALS_THRESHOLDS['spo2']['crit_low']}%)")
        elif vitals.spo2 is not None and vitals.spo2 < VITALS_THRESHOLDS["spo2"]["warn_low"]:
            hypoxia_triggers.append(f"Moderate Hypoxemia: SpO2 {vitals.spo2:.1f}% (< {VITALS_THRESHOLDS['spo2']['warn_low']}%)")

        if environment:
            if environment.o2_percent < ENVIRONMENT_THRESHOLDS["o2_percent"]["crit_low"]:
                hypoxia_triggers.append(f"Critical Cabin O2 Depletion: {environment.o2_percent:.1f}% (< {ENVIRONMENT_THRESHOLDS['o2_percent']['crit_low']}%)")
            elif environment.o2_percent < ENVIRONMENT_THRESHOLDS["o2_percent"]["warn_low"]:
                hypoxia_triggers.append(f"Low Cabin O2: {environment.o2_percent:.1f}% (< {ENVIRONMENT_THRESHOLDS['o2_percent']['warn_low']}%)")
            
            if environment.cabin_pressure_kpa < ENVIRONMENT_THRESHOLDS["cabin_pressure"]["crit_low"]:
                hypoxia_triggers.append(f"Severe Decompression: {environment.cabin_pressure_kpa:.1f} kPa (< {ENVIRONMENT_THRESHOLDS['cabin_pressure']['crit_low']} kPa)")

        if hypoxia_triggers:
            is_critical = (vitals.spo2 is not None and vitals.spo2 < VITALS_THRESHOLDS["spo2"]["crit_low"]) or \
                          (environment and (environment.o2_percent < 18.0 or environment.cabin_pressure_kpa < 90.0))
            level = "CRITICAL" if is_critical else "MODERATE"
            alerts.append(HealthAlert(
                astronaut_id=ast_id,
                alert_level=level,
                category="Respiratory & Cabin Atmosphere",
                title="Hypoxia / Cabin Decompression Alert",
                description="Oxygen delivery or habitat pressure is below safe operational physiological thresholds.",
                triggering_indicators=hypoxia_triggers,
                missing_indicators=["Arterial Blood Gas (ABG)" if vitals.spo2 is None else ""],
                recommended_action="IMMEDIATE ACTION: Don oxygen mask (100% O2). Verify habitat pressure seal. Recline crew member."
            ))

        # 2. Cardiovascular Risk Assessment
        cv_triggers = []
        if vitals.heart_rate is not None:
            if vitals.heart_rate >= VITALS_THRESHOLDS["heart_rate"]["crit_high"]:
                cv_triggers.append(f"Critical Tachycardia: {vitals.heart_rate:.0f} bpm (>= {VITALS_THRESHOLDS['heart_rate']['crit_high']})")
            elif vitals.heart_rate <= VITALS_THRESHOLDS["heart_rate"]["crit_low"]:
                cv_triggers.append(f"Severe Bradycardia: {vitals.heart_rate:.0f} bpm (<= {VITALS_THRESHOLDS['heart_rate']['crit_low']})")
            elif vitals.heart_rate >= VITALS_THRESHOLDS["heart_rate"]["warn_high"]:
                cv_triggers.append(f"Elevated Heart Rate: {vitals.heart_rate:.0f} bpm (>= {VITALS_THRESHOLDS['heart_rate']['warn_high']})")

        if vitals.sys_bp is not None:
            if vitals.sys_bp >= VITALS_THRESHOLDS["sys_bp"]["crit_high"]:
                cv_triggers.append(f"Hypertensive Crisis: Sys BP {vitals.sys_bp:.0f} mmHg")
            elif vitals.sys_bp <= VITALS_THRESHOLDS["sys_bp"]["crit_low"]:
                cv_triggers.append(f"Hypotensive Shock Warning: Sys BP {vitals.sys_bp:.0f} mmHg")

        if cv_triggers:
            is_critical = any("Critical" in t or "Crisis" in t or "Shock" in t for t in cv_triggers)
            alerts.append(HealthAlert(
                astronaut_id=ast_id,
                alert_level="CRITICAL" if is_critical else "MODERATE",
                category="Cardiovascular",
                title="Cardiovascular Instability Indicator",
                description="Heart rate and/or systemic arterial pressures deviate significantly from mission baseline.",
                triggering_indicators=cv_triggers,
                missing_indicators=["12-Lead Holter ECG", "Cardiac Ultrasound"],
                recommended_action="Cease exercise, place astronaut in resting posture, initiate 3-lead rhythm ECG monitoring."
            ))

        # 3. Spaceflight Radiation Exposure
        if environment and environment.radiation_rate_usv_h >= ENVIRONMENT_THRESHOLDS["radiation_rate_usv_h"]["warn_high"]:
            is_crit = environment.radiation_rate_usv_h >= ENVIRONMENT_THRESHOLDS["radiation_rate_usv_h"]["crit_high"]
            alerts.append(HealthAlert(
                astronaut_id=ast_id,
                alert_level="CRITICAL" if is_crit else "MODERATE",
                category="Space Radiation",
                title="Solar Particle Event / Acute Radiation Influx",
                description=f"Spacecraft dosimeters indicate ambient radiation flux of {environment.radiation_rate_usv_h:.1f} µSv/h.",
                triggering_indicators=[f"Radiation Rate {environment.radiation_rate_usv_h:.1f} µSv/h (Threshold: {ENVIRONMENT_THRESHOLDS['radiation_rate_usv_h']['warn_high']} µSv/h)"],
                missing_indicators=["Personal Biodosimetry Blood Chromosomal Assay"],
                recommended_action="SOUND RADIATION ALARM: Move all crew to Storm Shelter core. Verify polyethylene/water shielding."
            ))

        # 4. Hypercapnia (Elevated CO2)
        if environment and environment.co2_mmhg >= ENVIRONMENT_THRESHOLDS["co2_mmhg"]["warn_high"]:
            is_crit = environment.co2_mmhg >= ENVIRONMENT_THRESHOLDS["co2_mmhg"]["crit_high"]
            alerts.append(HealthAlert(
                astronaut_id=ast_id,
                alert_level="CRITICAL" if is_crit else "MODERATE",
                category="Environmental Toxicology",
                title="Elevated Cabin CO2 (Hypercapnia Risk)",
                description=f"Partial pressure of carbon dioxide reached {environment.co2_mmhg:.1f} mmHg.",
                triggering_indicators=[f"Cabin CO2: {environment.co2_mmhg:.1f} mmHg (Normal <= {ENVIRONMENT_THRESHOLDS['co2_mmhg']['normal_max']} mmHg)"],
                missing_indicators=["Capnography end-tidal CO2"],
                recommended_action="Inspect amine/LiOH scrubber beds, activate backup ECLSS atmospheric loop, minimize physical exertion."
            ))

        # 5. Core Temperature & Thermoregulation
        if vitals.temperature is not None:
            if vitals.temperature >= VITALS_THRESHOLDS["temperature"]["crit_high"]:
                alerts.append(HealthAlert(
                    astronaut_id=ast_id,
                    alert_level="CRITICAL",
                    category="Thermoregulation / Infectious",
                    title="Severe Hyperthermia / High Pyrexia",
                    description=f"Core temperature reached {vitals.temperature:.1f} °C.",
                    triggering_indicators=[f"Core Temp {vitals.temperature:.1f} °C (Crit > {VITALS_THRESHOLDS['temperature']['crit_high']} °C)"],
                    missing_indicators=["Blood culture panel", "Thermal imaging"],
                    recommended_action="Apply evaporative cooling, hydrate, administer antipyretic protocol as approved by Flight Surgeon."
                ))
            elif vitals.temperature <= VITALS_THRESHOLDS["temperature"]["crit_low"]:
                alerts.append(HealthAlert(
                    astronaut_id=ast_id,
                    alert_level="CRITICAL",
                    category="Thermoregulation",
                    title="Accidental Hypothermia Alert",
                    description=f"Core body temperature dropped to {vitals.temperature:.1f} °C.",
                    triggering_indicators=[f"Core Temp {vitals.temperature:.1f} °C (Crit <= {VITALS_THRESHOLDS['temperature']['crit_low']} °C)"],
                    missing_indicators=["Continuous esophageal temp probe"],
                    recommended_action="Wrap in aluminized space blanket, apply trunk warm packs, heat cabin sector to 25°C."
                ))

        # 6. Camera Screening Correlation (Fatigue / Eye Strain / Motor Coordination)
        if camera_obs:
            cam_triggers = []
            if camera_obs.blink_rate_per_min > 35.0:
                cam_triggers.append(f"Elevated Blink Frequency: {camera_obs.blink_rate_per_min:.1f}/min (Normal: 12-24/min)")
            if camera_obs.tracking_error_px > 45.0:
                cam_triggers.append(f"Visual Smooth Pursuit Tracking Error: {camera_obs.tracking_error_px:.1f}px (Degraded motor response)")
            if camera_obs.reaction_time_ms > 450.0:
                cam_triggers.append(f"Prolonged Visual Reaction Latency: {camera_obs.reaction_time_ms:.0f}ms (Baseline: 240-300ms)")
            if camera_obs.facial_asymmetry_pct > 25.0:
                cam_triggers.append(f"Facial Landmark Asymmetry: {camera_obs.facial_asymmetry_pct:.1f}%")

            if cam_triggers:
                is_crit = camera_obs.facial_asymmetry_pct > 35.0
                alerts.append(HealthAlert(
                    astronaut_id=ast_id,
                    alert_level="CRITICAL" if is_crit else "MODERATE",
                    category="Neuro-Vestibular & Fatigue Screening",
                    title="Visual Screening Functional Abnormality",
                    description="Optical landmark analysis and tracking performance suggest neuro-vestibular strain or acute fatigue.",
                    triggering_indicators=cam_triggers,
                    missing_indicators=["In-person neurological cranial nerve exam", "High-res fundus photography"],
                    recommended_action="Administer manual neurological check, review sleep debt, schedule rest period, consult CMO."
                ))

        # 7. Symptoms Correlation
        if symptoms:
            for s in symptoms:
                if s.get("severity") == "SEVERE":
                    alerts.append(HealthAlert(
                        astronaut_id=ast_id,
                        alert_level="CRITICAL",
                        category=f"Symptom Escalation: {s.get('category')}",
                        title=f"Severe Symptom Reported: {s.get('category')}",
                        description=s.get("description", "Severe symptom logged by astronaut."),
                        triggering_indicators=[f"Category: {s.get('category')}", f"Severity: {s.get('severity')}"],
                        missing_indicators=[],
                        recommended_action="Initiate emergency clinical evaluation protocol. Consult Flight Surgeon."
                    ))

        # Persist alerts to database
        self._record_alerts(alerts)
        return alerts

    def _record_alerts(self, alerts: List[HealthAlert]):
        """Saves generated alerts to SQLite database."""
        for alert in alerts:
            try:
                db_manager.execute_write(
                    "INSERT INTO health_alerts (astronaut_id, timestamp, alert_level, category, title, description, triggering_indicators, missing_indicators, recommended_action, acknowledged) "
                    "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",
                    (
                        alert.astronaut_id,
                        alert.timestamp,
                        alert.alert_level,
                        alert.category,
                        alert.title,
                        alert.description,
                        ", ".join(alert.triggering_indicators),
                        ", ".join(alert.missing_indicators),
                        alert.recommended_action
                    )
                )
            except Exception as e:
                print(f"Failed to record alert: {e}")


risk_engine = RiskEngine()
