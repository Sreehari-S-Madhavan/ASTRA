# ASTRA: Module Documentation

This document describes the software structure, class responsibilities, and public interfaces of each core module in ASTRA.

---

## 1. Core Subsystem (`astra.core`)

### `auth.py`
- **Class `Role`**: Constants for `FLIGHT_SURGEON`, `CREW_MEDICAL_OFFICER`, `ASTRONAUT`, and `MISSION_CONTROLLER`.
- **Class `SessionManager`**: Tracks active authenticated user credentials, role permissions, and active medical workstation station.
- **Function `hash_password(password, salt)`**: PBKDF2-HMAC-SHA256 password hashing with 100,000 iterations.
- **Function `verify_password(password, salt_hex, expected_hash_hex)`**: Cryptographically secure digest comparison.

### `audit.py`
- **Function `log_audit(action, target_entity, details)`**: Formats an immutable audit record and commits it to `system_audit_logs`.

### `event_bus.py`
- **Class `EventBus(QObject)`**: Central Qt signal dispatcher exposing signals:
  - `vitals_updated`: Real-time biometric payload.
  - `environment_updated`: ECLSS atmospheric payload.
  - `hazard_detected`: Spaceflight hazard breach.
  - `alert_generated`: Clinical risk alert.
  - `emergency_activated`: Emergency protocol state machine change.
  - `emergency_resolved`: Resolution notification.
  - `camera_assessment_completed`: Screening test completion.
  - `companion_message_requested`: Companion speech/mood request.
  - `message_status_changed`: DSN transmission status change.
  - `active_astronaut_changed`: Active crew context change.

---

## 2. Computer Vision Subsystem (`astra.cv`)

### `camera_manager.py`
- **Class `CameraQualityMetrics`**: Static evaluation of frame brightness, contrast, and Laplacian sharpness variance.
- **Class `CameraThread(QThread)`**: Dedicated worker thread capturing frames at ~30 FPS from physical webcam or procedural synthetic astronaut generator.
  - Methods: `start()`, `stop()`, `pause()`, `resume()`, `toggle_synthetic()`.

### `vision_engine.py`
- **Class `VisionEngine`**: Core optical landmark and geometric analysis engine.
  - Methods:
    - `process_frame(frame, draw_overlays, enable_rppg)`: Detects face bounding box, computes Eye Aspect Ratio (EAR), detects blinks, calculates rolling blink frequency, estimates 3D head pose (Pitch, Yaw, Roll via `solvePnP`), evaluates facial asymmetry %, and estimates rPPG green-channel pulse.
    - `reset_screening_stats()`: Resets blink counters and session buffers.

### `visual_tests.py`
- **Class `VisualTrackingTest(QObject)`**: Calibrated sinusoidal moving target for smooth pursuit tracking error calculation.
- **Class `VisualReactionTest(QObject)`**: Randomized visual stimulus display measuring cognitive reflex reaction latency in milliseconds.
- **Class `GuidedCoordinationTest(QObject)`**: Multi-axis head rotational drill detecting vestibular motor incoordination.

---

## 3. Health & Hazards Subsystems (`astra.health`)

### `risk_engine.py`
- **Class `RiskEngine`**: Rule-based transparent risk assessment engine.
  - Method `evaluate(vitals, environment, camera_obs, symptoms)`: Evaluates multi-source telemetry against clinical aerospace safety boundaries and returns structured `HealthAlert` instances.

### `hazard_engine.py`
- **Class `HazardEngine`**: Evaluates telemetry against the five primary spaceflight hazards: Space Radiation, Isolation/Confinement, Distance from Earth, Gravity Fields, and Hostile Environments.

---

## 4. Emergency Subsystem (`astra.emergency`)

### `emergency_manager.py`
- **Class `EmergencyManager`**: Controls zero-navigation life-support workflows, incident state machines, and triage.
  - Methods: `activate_emergency()`, `log_action_step()`, `update_status()`, `get_active_incident()`.

### `protocols.py`
- **Class `MedicalProtocolsRegistry`**: Registry of 10 fictional, unvalidated example workflows.

---

## 5. Telecommunications Subsystem (`astra.physician`)

### `comm_manager.py`
- **Class `CommunicationManager(QObject)`**: Manages store-and-forward transmission queues, simulated light-time radio delay, and ground station auto-acknowledgements.
  - Methods: `send_message()`, `set_comm_delay()`, `set_offline_mode()`, `get_active_queue()`.

### `server.py`
- **FastAPI Application**: Ground Mission Control telemetry and report receiver station.

---

## 6. Reporting Subsystem (`astra.reporting`)

### `report_generator.py`
- **Class `ReportGenerator`**: Generates publication-quality PDF medical dossiers featuring telemetry snapshots, ECLSS tables, screening results, and physician signature blocks.

---

## 7. Simulation Subsystem (`astra.simulation`)

### `mission_simulator.py`
- **Class `MissionSimulator(QObject)`**: Generates continuous mission telemetry ticks with realistic noise and drives 12 predefined mission anomaly scenarios.
