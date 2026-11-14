# ASTRA: Testing & Quality Assurance Documentation

## 1. Test Architecture
ASTRA includes an automated test suite verifying core functional workflows:
- Database schema, table indexes, and foreign key constraint enforcement.
- Rule-based risk evaluation engine threshold logic (Hypoxia, Tachycardia, Pyrexia, Sensor disconnection).
- Spaceflight hazard monitors (Radiation flux, Isolation fatigue, ECLSS closed environment anomalies).
- Emergency activation lifecycle, checklist action logging, and status transitions.
- Computer vision frame processing, Eye Aspect Ratio (EAR), blink detection, and visual tests.
- DSN communication queue latency simulation and Flight Surgeon auto-acknowledgements.
- Native publication-quality PDF medical dossier generation.
- Mission simulation scenario loading and speed scaling.

## 2. Test Execution & Results
Execute the automated test suite from the repository root:
```bash
python run_tests.py
```

### Verified Test Matrix (18 Tests, 100% Pass Rate)

| Test Module | Test Case | Status | Verified Functionality |
| :--- | :--- | :--- | :--- |
| `test_database` | `test_schema_initialization` | **PASSED** | Verifies all 14 database tables exist with indexed fields. |
| `test_database` | `test_foreign_key_enforcement` | **PASSED** | Verifies SQLite rejects orphan astronaut records. |
| `test_risk_engine` | `test_nominal_evaluation` | **PASSED** | Confirms normal vitals produce zero critical alerts. |
| `test_risk_engine` | `test_critical_hypoxia_detection` | **PASSED** | Triggers critical alert when SpO2 < 85% or Pressure < 85 kPa. |
| `test_risk_engine` | `test_tachycardia_cardiovascular_detection` | **PASSED** | Triggers alert when HR >= 140 bpm. |
| `test_risk_engine` | `test_sensor_disconnection` | **PASSED** | Flags sensor integrity alert when leads detach. |
| `test_hazards` | `test_space_radiation_hazard` | **PASSED** | Detects SPE flux > 100 µSv/h and assigns storm shelter mitigation. |
| `test_hazards` | `test_eclss_environmental_hazard` | **PASSED** | Flags critical life-support loop anomaly when CO2 > 5.5 mmHg. |
| `test_hazards` | `test_isolation_fatigue_hazard` | **PASSED** | Flags fatigue warning when sleep < 5h and fatigue >= 7. |
| `test_emergency` | `test_protocol_retrieval` | **PASSED** | Confirms 10 illustrative sample emergency workflows exist. |
| `test_emergency` | `test_emergency_activation_and_resolution` | **PASSED** | Verifies 1-click activation, action logging, and resolution. |
| `test_vision` | `test_camera_quality_metrics` | **PASSED** | Evaluates frame brightness, contrast, and sharpness variance. |
| `test_vision` | `test_vision_engine_frame_processing` | **PASSED** | Confirms extraction of EAR, blinks, and 3D head pose angles. |
| `test_vision` | `test_guided_visual_tracking_test` | **PASSED** | Evaluates Euclidean tracking error for moving targets. |
| `test_vision` | `test_visual_reaction_test` | **PASSED** | Measures millisecond stimulus reflex reaction latency. |
| `test_communication` | `test_comm_queue_dispatch` | **PASSED** | Verifies message enqueuing and store-and-forward. |
| `test_communication` | `test_medical_report_pdf_generation`| **PASSED** | Generates real vector PDF medical dossier on disk. |
| `test_communication` | `test_mission_simulator_scenario_load` | **PASSED** | Verifies instant scenario loading and parameter injection. |

**Result Summary**: `18 passed in 0.585s` (0 errors, 0 failures).
