# ASTRA • Astronaut Health & Safety Monitoring System

**ASTRA (Astronaut Health & Safety Monitoring System)** is an integrated, offline-capable aerospace medical workstation engineered for long-duration deep space exploration missions (such as Mars transit and Lunar Gateway surface operations).

ASTRA addresses the physiological, environmental, and neuro-vestibular challenges of long-duration spaceflight by uniting real-time biometric telemetry, computer vision-based visual screening, spaceflight hazard monitoring, transparent rule-based risk evaluation, emergency triage protocols, remote physician telecommunication with interplanetary light-time propagation delay, and an original animated space companion.

> **Prototype notice:** ASTRA is a software demonstration, not a medical device or source of medical advice. Seed profiles, telemetry, contacts, and emergency workflows are fictional examples and have not been clinically validated or approved. Do not use the workflows for real patient care or deploy this prototype with real health data.

---

## Key Capabilities & Architecture

1. **Camera-Based Health & Visual Screening Suite (Primary Priority)**:
   - Real-time face detection, eye landmark tracking, and Eye Aspect Ratio (EAR) blink rate frequency observations.
   - On-screen face-position grid and live framing, distance, and lighting guidance; camera rotation and selfie mirroring controls.
   - 3D Head Pose Estimation (Pitch, Yaw, Roll) using Perspective-n-Point (`solvePnP`) projection.
   - Bilateral facial landmark symmetry analysis.
   - Camera quality, sharpness, illumination, and contrast assessment.
   - Interactive Guided Visual Tests:
     - **Guided Eye Tracking Test**: Sinusoidal smooth pursuit target with Euclidean tracking error scoring.
     - **Visual Reaction-Time Test**: Randomized stimulus triggering with millisecond reflex latency recording.
     - **Guided Coordination Test**: Multi-axis head rotational drill detecting vestibular motor incoordination.
     - **Disconnect & Synthetic Testing**: Realistic procedural astronaut test feed allowing volunteer and offline testing.
     - **Experimental rPPG**: Forehead green-channel photoplethysmography pulse estimation labeled clearly for research demonstration.

2. **Physiological Health Monitoring & Hazard Mitigation**:
   - Continuous telemetry for Heart Rate, SpO2, Blood Pressure, Core Temperature, Respiratory Rate, and Hydration.
   - Clinical symptom logging with category, severity grading, and context notes.
   - Comprehensive monitoring of the **Five Spaceflight Hazards**:
     - *Space Radiation*: SPE dosimeter flux alerts & storm shelter protocols.
     - *Isolation & Confinement*: Circadian rhythm disruption, sleep debt, and fatigue scores.
     - *Distance from Earth*: Interplanetary communication delay and offline autonomous store-and-forward.
     - *Gravity Fields*: Microgravity vestibular ataxia, motor saccades, and SANS monitoring.
     - *Hostile & Closed Environments*: ECLSS cabin O2, CO2 partial pressure, and pressure integrity.

3. **Transparent Rule-Based Risk Assessment Engine**:
   - Deterministic, multi-indicator clinical logic avoiding unvalidated black-box AI models.
   - Explicit breakdown of triggering indicators, unmonitored/missing sensors, and required actions.
   - Alerts classified into `LOW`, `MODERATE`, and `CRITICAL`.

4. **Zero-Navigation Emergency Workflow Demonstrations**:
   - 10 fictional example workflows (Hypoxia/Decompression, Cardiac/Chest Pain, Syncope, Hemorrhage, Radiation Event, Toxic Contamination, Severe Motion Sickness, SANS, Hypothermia, Dehydration).
   - Interactive sample checklist with audit logging.
   - Example contraindications and escalation criteria; not clinically approved.

5. **Interplanetary Physician Communications & Reports**:
   - Simulated Deep Space Network (DSN) light-time radio delay (configurable 0s to 20 mins).
   - Transmission queue tracking: `DRAFT` -> `QUEUED` -> `TRANSMITTING` -> `DELIVERED` -> `ACKNOWLEDGED`.
   - Native publication-quality PDF medical dossier generation.
   - Ground station Flight Surgeon review and digital signature simulation.

6. **Original Animated Space Companion ("Astraea")**:
   - Procedural vector-animated cosmic celestial creature rendered via PySide6 `QPainter`.
   - 7 Emotional and operational states: *Idle, Talking, Listening, Thinking, Happy, Concerned, Emergency Alert*.
   - Non-blocking offline text-to-speech and one-utterance microphone commands through Windows Speech Recognition; audio stays on-device.
   - Typed natural-language commands remain available on all supported platforms.

7. **Integrated Mission Simulation Environment**:
   - 12 Selectable operational and anomaly scenarios (Nominal, Tachycardia, Hypoxia, Hypercapnia, Radiation Storm, Dehydration, Sensor Disconnect, Comm Failure, etc.).
   - Speed scaling (0.5x, 1x, 2x, 5x, 10x) and manual sliders for all biometric and environmental parameters.

---

## Quick Start & Installation

### Requirements
- Windows 10/11, Linux, or macOS
- Python 3.10+
- Install dependencies with `python -m pip install -r requirements.txt`
- OpenCV is needed for face detection; the application can start without it, but camera screening is limited.

### Launching the Application
```bash
# Create a virtual environment once
python -m venv .venv

# Activate it, then install dependencies
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Git Bash / Linux / macOS: source .venv/bin/activate
python -m pip install -r requirements.txt

# Run automated verification tests
python run_tests.py

# Launch the desktop workstation
python astra/main.py

# Or launch from any working directory with the location-independent script
bash /path/to/astra/run_astra.sh
```

On Windows, run `run_astra.sh` from Git Bash or WSL. The script uses a project-local `.venv` when present, otherwise it uses the Python interpreter on `PATH`. The application opens maximized; camera rotation and mirroring can be changed on the Camera Screening page.

On Windows, microphone commands use the local Windows Speech Recognition engine; the app does not send audio to a network speech service. Other platforms retain typed commands.

The optional FastAPI ground-station server is a local demonstration without authentication; do not expose it to a network or use it for real telemetry.

The desktop app also starts with a default demo operator session. Its role controls are prototype scaffolding, not production authentication or authorization.

---

## Project Structure
```
astra/
├── astra/
│   ├── config.py                 # Global constants, paths, thresholds, and dark space theme
│   ├── main.py                   # Desktop application entry point
│   ├── core/
│   │   ├── auth.py               # RBAC session manager, role permissions, password hashing
│   │   ├── audit.py              # System audit logger with immutable record keeping
│   │   └── event_bus.py          # Central Qt Signal / Slot event bus
│   ├── database/
│   │   ├── db_manager.py         # SQLite connection manager, schema migrations, foreign keys
│   │   ├── seed_data.py          # Seed data (astronauts, protocols, baselines, physicians)
│   │   └── models.py             # Data schema models and definitions
│   ├── cv/
│   │   ├── camera_manager.py     # OpenCV capture thread, quality metrics, synthetic test feed
│   │   ├── vision_engine.py      # Face detection, EAR blink detector, head pose PnP, asymmetry
│   │   └── visual_tests.py       # Guided eye-tracking, reaction latency, coordination tests
│   ├── health/
│   │   ├── models.py             # VitalSigns, EnvironmentalMetrics, CameraObservation dataclasses
│   │   ├── risk_engine.py        # Rule-based transparent risk assessment engine
│   │   └── hazard_engine.py      # 5 Spaceflight hazard evaluation engine
│   ├── emergency/
│   │   ├── emergency_manager.py  # Emergency activation, action logging, status lifecycle
│   │   └── protocols.py          # 10 fictional sample emergency workflows
│   ├── physician/
│   │   ├── comm_manager.py       # Interplanetary delay simulator, store-and-forward queue
│   │   └── server.py             # FastAPI ground telemetry station receiver
│   ├── reporting/
│   │   └── report_generator.py   # Publication-quality PDF medical dossier generator
│   ├── simulation/
│   │   └── mission_simulator.py  # 12 Mission anomaly scenarios & telemetry noise generator
│   ├── companion/
│   │   ├── companion_widget.py   # "Astraea" procedural vector avatar (7 states) & dialog
│   │   └── voice_engine.py       # Non-blocking TTS worker and voice command interpreter
│   ├── ui/
│   │   ├── theme.py              # Futuristic deep space dark workstation stylesheet
│   │   ├── main_window.py        # Main window shell, sidebar, alert banner, companion drawer
│   │   ├── widgets/              # Metric cards, alert banner, trend graph, camera viewport
│   │   └── views/                # 11 Modular application views
│   └── tests/                    # Automated unit and integration tests
├── docs/                         # Comprehensive architectural and technical documentation
├── requirements.txt              # Python dependencies
├── run_astra.sh                  # Location-independent launcher
└── run_tests.py                  # Test runner script
```
