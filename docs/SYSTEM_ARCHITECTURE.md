# ASTRA: System Architecture

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------------+
|                                    ASTRA WORKSTATION                                    |
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |                            TOP ALERT & STATUS BANNER                              |  |
|  +-----------------------------------------------------------------------------------+  |
|                                                                                         |
|  +----------------+  +--------------------------------------------+  +---------------+  |
|  | SIDEBAR NAV    |  |        STACKED MODULE VIEWPORTS            |  | COMPANION     |  |
|  |                |  |                                            |  |               |  |
|  | • Overview     |  |  [0] Mission Overview Dashboard            |  |  "Astraea"    |  |
|  | • Camera ★     |  |  [1] Camera-Based Visual Screening Suite   |  |  Procedural   |  |
|  | • Health Vitals|  |  [2] Physiological Health Monitoring       |  |  Vector Avatar|  |
|  | • Hazards (5)  |  |  [3] Spaceflight Hazard Console            |  |  (7 Moods)   |  |
|  | • Risk Engine  |  |  [4] Rule-Based Health Risk Assessment     |  |               |  |
|  | • Emergency    |  |  [5] Zero-Navigation Emergency Protocols   |  |  Voice Engine |  |
|  | • Reports (PDF)|  |  [6] Medical Dossiers & PDF Generation     |  |  Offline TTS  |  |
|  | • Ground Comms |  |  [7] Physician Telecommunication Center   |  |  Command Parse|  |
|  | • Simulator    |  |  [8] Mission Simulation Environment        |  +---------------+  |
|  | • Profile      |  |  [9] Astronaut Baselines & Profile         |                     |
|  | • Settings     |  |  [10] Workstation Settings, RBAC & Audit   |                     |
|  +----------------+  +--------------------------------------------+                     |
|                                                                                         |
|  +-----------------------------------------------------------------------------------+  |
|  |                      CENTRAL DECOUPLED EVENT BUS (Qt Signals)                     |  |
|  +-----------------------------------------------------------------------------------+  |
|          ^                  ^                  ^                  ^               ^     |
|          |                  |                  |                  |               |     |
|  +-------+-------+  +-------+-------+  +-------+-------+  +-------+-------+  +----+---+ |
|  | Computer      |  | Health &      |  | Emergency     |  | Ground Comm   |  | SQLite | |
|  | Vision Engine |  | Hazard Engine |  | Manager       |  | Store-Forward |  | DB &   | |
|  | (OpenCV / CV) |  | (Rules Logic) |  | (Protocols)   |  | (DSN Delay)   |  | Audit  | |
|  +---------------+  +---------------+  +---------------+  +---------------+  +--------+ |
+-----------------------------------------------------------------------------------------+
                                          |
                                   (Simulated DSN Link)
                                          v
                      +---------------------------------------+
                      |   GROUND MISSION CONTROL (FastAPI)    |
                      |   Flight Surgeon Ingestion Console    |
                      +---------------------------------------+
```

## 2. Decoupled Communication Model
The system uses a publish-subscribe event bus architecture (`astra.core.event_bus.bus`) implemented on top of PySide6 `QObject` signals. This guarantees:
- **Thread Safety**: High-frequency video capture (~30 FPS) and simulation telemetry ticks run in background threads without blocking UI event loops.
- **Loose Coupling**: Telemetry producers (Mission Simulator, Sensors, Camera Engine) do not have direct dependencies on UI views.
- **Extensibility**: Additional hardware sensor adapters can be plugged directly into the event bus.

## 3. Core Subsystems
1. **Core Application Controller (`astra.ui.main_window`)**: Manages navigation routing, top emergency banner triage, companion drawer, and system life cycle.
2. **Computer Vision Subsystem (`astra.cv`)**: Manages real-time webcam frame acquisition, camera quality evaluation, procedural synthetic astronaut fallback, landmark processing, EAR blink analysis, head pose estimation, and interactive visual tests.
3. **Health & Hazard Assessment Engine (`astra.health`)**: Houses clinical aerospace threshold baselines, rule-based risk evaluation logic, and hazard mitigation evaluators.
4. **Emergency Subsystem (`astra.emergency`)**: Provides immediate zero-navigation protocol lookup, step-by-step checklist logging, and escalation dispatches.
5. **Physician Communication & Telemetry (`astra.physician`)**: Simulates light-time communication latency, store-and-forward message queues, and Flight Surgeon acknowledgements.
6. **Reporting Engine (`astra.reporting`)**: Compiles telemetry, hazard logs, and screening results into formal vector-rendered PDF medical dossiers.
7. **Virtual Companion (`astra.companion`)**: Procedural vector character with 7 operational states and speech synthesis hooks.
