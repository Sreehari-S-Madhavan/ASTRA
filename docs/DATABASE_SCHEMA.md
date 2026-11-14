# ASTRA: Database Schema & Entity Relational Architecture

The system utilizes an embedded relational SQLite database with strict foreign-key enforcement (`PRAGMA foreign_keys = ON`), indexed query optimization, and structured audit trails.

## Table Definitions

### 1. `missions`
Tracks deep space operational missions and current phases.
- `id` (TEXT, PK): Unique mission identifier (e.g. `M-ARES5`).
- `name` (TEXT): Full operational title.
- `spacecraft` (TEXT): Spacecraft designation.
- `destination` (TEXT): Target planetary or orbital body.
- `launch_date` (TEXT): ISO 8601 launch timestamp.
- `duration_days` (INTEGER): Planned mission duration.
- `current_phase` (TEXT): Operational phase (e.g. `Transit to Mars`).
- `status` (TEXT): Status (`ACTIVE`, `COMPLETED`, `STANDBY`).

### 2. `astronauts`
Stores crew identities, flight roles, and individual physiological baselines.
- `id` (TEXT, PK): Crew identifier (e.g. `AST-01`).
- `callsign` (TEXT, UNIQUE): Radiotelephone tactical callsign.
- `name` (TEXT): Full name and credentials.
- `age` (INTEGER): Crew member age.
- `role` (TEXT): Mission assignment.
- `mission_id` (TEXT, FK -> `missions.id`): Active mission reference.
- `baseline_hr`, `baseline_spo2`, `baseline_sys_bp`, `baseline_dia_bp`, `baseline_temp`, `baseline_resp` (REAL): Calibrated baselines.
- `medical_summary` (TEXT): Authorized medical history.
- `created_at` (TEXT): Profile creation timestamp.

### 3. `health_readings`
Time-series physiological vital signs.
- `id` (INTEGER, PK AUTOINCREMENT)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `heart_rate`, `spo2`, `sys_bp`, `dia_bp`, `temperature`, `respiratory_rate`, `hydration_index`, `sleep_hours`, `fatigue_score` (REAL)
- `source_type` (TEXT): `SIMULATED` or `SENSOR`.
- `validity_status` (TEXT): `VALID`, `DEGRADED`, `INVALID`.
- `sensor_connected` (INTEGER): 1 if connected, 0 if lead detached.
- `notes` (TEXT): Operational remarks.

### 4. `symptom_reports`
Subjective astronaut symptom logs.
- `id` (INTEGER, PK AUTOINCREMENT)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `category` (TEXT): Affected anatomical/clinical system.
- `severity` (TEXT): `MILD`, `MODERATE`, `SEVERE`.
- `description` (TEXT): Detailed crew description.
- `duration_hours` (REAL): Symptom duration.
- `reported_by` (TEXT): Reporting operator.

### 5. `camera_assessments`
Optical computer vision visual screening session records.
- `id` (INTEGER, PK AUTOINCREMENT)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `assessment_type` (TEXT): `ROUTINE_SCREENING`, `EYE_TRACKING`, etc.
- `blink_count` (INTEGER): Detected blinks.
- `blink_rate_per_min` (REAL): Rolling blink frequency.
- `ear_avg` (REAL): Average Eye Aspect Ratio.
- `head_pitch`, `head_yaw`, `head_roll` (REAL): Euler angles.
- `facial_asymmetry_pct` (REAL): Landmark asymmetry percentage.
- `quality_score` (REAL): Frame sharpness/illumination score (0-100).
- `tracking_error_px` (REAL): Smooth pursuit distance error.
- `reaction_time_ms` (REAL): Reaction latency in milliseconds.
- `status` (TEXT): `COMPLETED`, `ABORTED`.

### 6. `environmental_readings`
ECLSS habitat life-support telemetry.
- `id` (INTEGER, PK AUTOINCREMENT)
- `timestamp` (TEXT)
- `o2_percent`, `co2_mmhg`, `cabin_pressure_kpa`, `cabin_temp_c`, `humidity_pct`, `radiation_rate_usv_h` (REAL)
- `system_status` (TEXT): `NOMINAL`, `WARNING`, `CRITICAL`.
- `notes` (TEXT)

### 7. `hazard_events`
Spaceflight hazard threshold excursion logs.
- `id` (INTEGER, PK AUTOINCREMENT)
- `timestamp` (TEXT)
- `hazard_category` (TEXT): `SPACE_RADIATION`, `ISOLATION_CONFINEMENT`, etc.
- `severity` (TEXT): `INFO`, `WARNING`, `CRITICAL`.
- `metric_name` (TEXT)
- `metric_value` (REAL)
- `threshold_breached` (TEXT)
- `mitigation_action` (TEXT)
- `resolved` (INTEGER)

### 8. `health_alerts`
Rule-based clinical risk evaluations.
- `id` (INTEGER, PK AUTOINCREMENT)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `alert_level` (TEXT): `LOW`, `MODERATE`, `CRITICAL`.
- `category` (TEXT)
- `title` (TEXT)
- `description` (TEXT)
- `triggering_indicators` (TEXT): Comma-separated list of values.
- `missing_indicators` (TEXT): Missing sensor fields.
- `recommended_action` (TEXT)
- `acknowledged` (INTEGER)

### 9. `medical_protocols`
Clinical emergency guidelines registry.
- `id` (TEXT, PK): Protocol ID (e.g. `PROT-01`).
- `code` (TEXT, UNIQUE): Standard mnemonic (e.g. `EMERG-HYPOXIA`).
- `title` (TEXT)
- `category` (TEXT)
- `observable_signs` (TEXT)
- `immediate_safety` (TEXT)
- `first_aid_steps` (TEXT): Numbered procedural steps.
- `contraindications` (TEXT): Actions to avoid.
- `escalation_criteria` (TEXT)
- `required_telemetry` (TEXT)
- `approved_by` (TEXT)
- `version` (TEXT)

### 10. `emergency_incidents`
Active and historical emergency interventions.
- `id` (INTEGER, PK AUTOINCREMENT)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `protocol_id` (TEXT, FK -> `medical_protocols.id`)
- `incident_type` (TEXT)
- `status` (TEXT): `ACTIVE`, `STABILIZED`, `RESOLVED`, `ESCALATED`.
- `initial_vitals` (TEXT): JSON snapshot.
- `actions_taken` (TEXT): JSON array of completed steps.
- `escalation_sent` (INTEGER)
- `physician_notified` (INTEGER)
- `resolved_at` (TEXT)

### 11. `physician_profiles`
Terrestrial and orbital flight surgeon roster.
- `id` (TEXT, PK)
- `name` (TEXT)
- `role` (TEXT)
- `callsign` (TEXT, UNIQUE)
- `ground_station` (TEXT)
- `email` (TEXT)
- `specialization` (TEXT)
- `availability_status` (TEXT)

### 12. `medical_reports`
Generated diagnostic dossiers.
- `id` (INTEGER, PK AUTOINCREMENT)
- `report_uid` (TEXT, UNIQUE)
- `astronaut_id` (TEXT, FK -> `astronauts.id`)
- `timestamp` (TEXT)
- `report_type` (TEXT)
- `severity` (TEXT)
- `summary` (TEXT)
- `vitals_snapshot` (TEXT): JSON.
- `risk_summary` (TEXT): JSON.
- `camera_summary` (TEXT): JSON.
- `incident_id` (INTEGER)
- `transmission_status` (TEXT): `DRAFT`, `QUEUED`, `TRANSMITTING`, `DELIVERED`, `ACKNOWLEDGED`.
- `transmitted_at` (TEXT)
- `acknowledged_at` (TEXT)
- `pdf_path` (TEXT)

### 13. `communication_messages`
Interplanetary transmission packets.
- `id` (INTEGER, PK AUTOINCREMENT)
- `msg_uid` (TEXT, UNIQUE)
- `sender` (TEXT)
- `recipient` (TEXT)
- `timestamp` (TEXT)
- `message_type` (TEXT)
- `priority` (TEXT): `ROUTINE`, `URGENT`, `EMERGENCY`.
- `subject` (TEXT)
- `body` (TEXT)
- `payload_json` (TEXT)
- `simulated_delay_sec` (REAL)
- `status` (TEXT): `QUEUED`, `TRANSMITTING`, `DELIVERED`, `ACKNOWLEDGED`.
- `delivered_at` (TEXT)
- `acknowledged_at` (TEXT)

### 14. `system_audit_logs`
Immutable security and protocol audit records.
- `id` (INTEGER, PK AUTOINCREMENT)
- `timestamp` (TEXT)
- `user_callsign` (TEXT)
- `role` (TEXT)
- `action` (TEXT)
- `target_entity` (TEXT)
- `details` (TEXT)
- `ip_or_station` (TEXT)
