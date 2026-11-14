# ASTRA: Known Limitations & Future Scope Documentation

ASTRA is an unvalidated software prototype. Advanced hardware sensor integrations and clinical diagnostic capabilities are future work and are not represented as complete or clinically approved.

---

## 1. Prototype Limitations

### A. Computer Vision Diagnostics vs. Clinical Measurements
- **Visual Observations Only**: Camera-based monitoring produces objective visual observations (blink frequency, eye tracking adherence, head rotational axes, and landmark symmetry). It does **not** diagnose neurological disorders, radiation sickness, cardiovascular disease, or psychological depression.
- **Environmental Factors**: Lighting variation, low illumination, camera blur, or partial facial occlusion can degrade optical tracking. The system includes camera quality indicators and manual alternatives.
- **Experimental rPPG**: The remote photoplethysmography (rPPG) green-channel pulse estimation module is strictly an experimental research demonstration. It is not clinically calibrated and must not be used for diagnostic triage.

### B. Sensor Telemetry
- Ground workstations and ordinary laptop environments lack physical microgravity dosimeters, cabin pressure transducers, or arterial cannulas. Simulated telemetry feeds are clearly identified as `SIMULATED` in the database and user interface.

### C. Offline Speech Recognition
- Speech recognition depends on available operating system microphone permissions and local offline acoustic models. Full keyboard and touch interaction is provided as a primary alternative.

---

## 2. Future Scope Roadmap

The software architecture of ASTRA is designed to be extensible so the following capabilities can be incorporated as operational flight hardware matures:

1. **Spacecraft Physical Sensor Bus Integrations**:
   - Integration with MIL-STD-1553, CAN bus, and SpaceWire telemetry protocols for cabin oxygen, carbon dioxide, pressure, and temperature sensors.
2. **Radiation Dosimeter Hardware**:
   - Direct serial/USB telemetry acquisition from active silicon dosimeters and tissue-equivalent proportional counters (TEPC).
3. **Clinical-Grade Wearable Biosensors**:
   - Integration with multi-lead wireless Holter ECG patches, continuous bio-impedance hydration sensors, and continuous core temperature pills.
4. **Autonomous Medical Decision Support & Machine Learning**:
   - Deployment of validated machine-learning models trained on aerospace clinical data to provide predictive trajectory analysis for chronic spaceflight adaptation.
5. **Telemedicine 3D Telepresence**:
   - High-bandwidth point-cloud and volumetric holographic streaming for remote ground surgeon consultations during low-latency mission phases.
6. **Multi-Spacecraft Medical Coordination**:
   - Distributed consensus protocols for multi-vehicle surface expeditions and habitat clusters.
