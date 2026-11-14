# ASTRA: User Manual & Operational Workflows

## 1. Workstation Interface Layout

### Top Alert & Status Banner
- In nominal state: Displays green indicator (`ALL HABITAT & BIOMETRIC SYSTEMS MONITORED • NOMINAL STATUS`).
- In warning or critical state: Flashes amber or red with a direct one-click jump button (`ACTIVATE EMERGENCY TRIAGE` or `REVIEW RISK FACTORS`). Clicking this button immediately navigates to the relevant protocol.

### Left Sidebar Navigation
Direct access to all 11 workstation modules:
1. **Mission Overview**: System summary, active crew profile, high-level biometric vitals cards, real-time trend curves, and ECLSS life-support gauges.
2. **Camera Screening (Primary Priority)**: Live camera feed with face tracking brackets, eye landmark indicators, 3D head pose projection axes, real-time telemetry table, and interactive visual tests.
3. **Health Monitoring**: Detailed vitals cards, historical graphs, clinical symptom logging form, and recent telemetry history table.
4. **Space Hazards**: Five spaceflight hazard panels with interactive mitigation triggers.
5. **Risk Assessment**: Transparent rule-based clinical indicator breakdown, missing data tracking, and audit log.
6. **Emergency Response**: Zero-navigation life-support console featuring 10 one-click emergency protocols, step-by-step checklists, contraindication warnings, and Flight Surgeon escalation.
7. **Medical Reports**: Medical dossier compilation, native PDF export, and ground transmission.
8. **Ground Comms**: Physician roster, message composer, and transmission queue with simulated light-time latency countdown.
9. **Mission Simulator**: Scenario selector (12 scenarios), simulation speed scaling, and manual parameter sliders.
10. **Astronaut Profile**: Crew roster selector, individual physiological baseline metrics, and medical summary.
11. **Settings & Audit**: Operator role switching (RBAC), audio/voice preferences, and system audit logs.

### Right Companion Drawer ("Astraea")
- **Animated Vector Character**: Procedural celestial creature showing 7 emotional states (*Idle, Talking, Listening, Thinking, Happy, Concerned, Emergency Alert*).
- **Speech Bubble**: Context-sensitive guidance, health advice, and test instructions.
- **Voice / Natural Text Command Bar**: Type or speak commands (e.g. *"Check my health"*, *"Run eye screening"*, *"Open emergency"*, *"Generate report"*).

---

## 2. Step-by-Step Walkthroughs

### Workflow A: Conducting a Guided Camera Health Screening
1. Click **CAMERA SCREENING** on the sidebar.
2. Position your face in front of the webcam. Observe the face lock brackets, eye landmarks, and 3D head pose coordinate axes.
3. Check the camera quality meter at the bottom: verifies illumination, contrast, and sharpness.
4. Click **1. START GUIDED EYE-TRACKING**: Follow the moving cyan target with your gaze. Upon completion, ASTRA displays your average smooth pursuit tracking error in pixels and smoothness score.
5. Click **2. START VISUAL REACTION-TIME TEST**: Wait for the green stimulus to flash, then click immediately. ASTRA logs your millisecond reaction latency.
6. Click **3. START GUIDED HEAD-COORDINATION TEST**: Follow the 5 rotational orientation prompts (*Center, Pitch Up, Yaw Left, Yaw Right, Center*).
7. Click **LOG SCREENING TO MEDICAL RECORD** to commit the screening session into the astronaut's permanent medical database.

### Workflow B: Handling a Simulated Emergency
1. In the **MISSION SIMULATOR**, select the `HYPOXIA` scenario and click **INJECT SCENARIO TELEMETRY**.
2. Notice the top banner instantly turns red: `CRITICAL HEALTH ALERT: HYPOXIA / CABIN DECOMPRESSION ALERT`.
3. Click the red **ACTIVATE EMERGENCY TRIAGE** button on the banner.
4. The Emergency Console opens immediately:
   - Read the prominent directive: *Connect crew member to 100% normobaric oxygen via high-flow mask.*
   - Review Contraindications: *DO NOT allow active physical exertion.*
   - Check off mandatory checklist actions as they are performed.
   - Click **TRANSMIT EMERGENCY ALERT TO FLIGHT SURGEON** to dispatch a priority alert.
   - Click **GENERATE PRIORITY EMERGENCY MEDICAL DOSSIER** to compile a formal PDF report.
5. Once patient vitals normalize, click **STABILIZE & RESOLVE EMERGENCY** to archive the incident.
