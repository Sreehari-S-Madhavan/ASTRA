# ASTRA: Rule-Based Health Risk Assessment Engine

## 1. Design Rationale
Medical decision-making in deep space exploration cannot depend on opaque, unvalidated machine learning models. A black-box classifier cannot explain *why* an alert was generated or defend its reasoning to an onboard Crew Medical Officer.

ASTRA employs a **deterministic, rule-based clinical evaluation engine** that combines:
1. Multi-parameter physiological vitals.
2. Environmental life support (ECLSS) readings.
3. Optical camera screening observations.
4. Astronaut-reported symptoms.
5. Missing or unmonitored sensor data.

## 2. Operational Alert Tiers

| Alert Level | Meaning & Clinical Protocol |
| :--- | :--- |
| **LOW** | Routine health maintenance. All biometrics and life support parameters within nominal mission baselines. |
| **MODERATE** | Threshold excursion detected. Requires secondary clinical assessment, countermeasure adjustment, or diagnostic follow-up. |
| **CRITICAL** | Severe medical risk or environmental failure. Triggers immediate zero-navigation emergency workflow and dispatches priority ground alert. |

## 3. Evaluation Rules & Multi-Factor Triggers

### A. Hypoxia & Cabin Decompression
- **Triggers**:
  - $\text{SpO}_2 < 85\%$ (Critical) or $< 90\%$ (Moderate).
  - Cabin total pressure $< 85\text{ kPa}$ (Critical) or $< 94\text{ kPa}$ (Moderate).
  - Cabin $\text{O}_2 < 18.0\%$ (Critical) or $< 19.5\%$ (Moderate).
- **Explanation**: Oxygen delivery or habitat pressure is below safe operational physiological thresholds.
- **Mandatory Action**: Immediate donning of 100% oxygen mask. Verify pressure integrity. Recline crew member to 30°.

### B. Cardiovascular Instability
- **Triggers**:
  - Heart Rate $\ge 140\text{ bpm}$ or $\le 40\text{ bpm}$ (Critical).
  - Heart Rate $\ge 120\text{ bpm}$ or $\le 50\text{ bpm}$ (Moderate).
  - Systolic BP $\ge 160\text{ mmHg}$ or $\le 80\text{ mmHg}$ (Critical).
- **Explanation**: Cardiac workload or vascular resistance deviates significantly from mission baseline.
- **Mandatory Action**: Cease physical exercise, seat in semi-Fowler's posture, initiate 3-lead rhythm ECG monitoring.

### C. Solar Particle Event / Acute Radiation Influx
- **Triggers**:
  - Ambient dosimeter flux $\ge 100\text{ }\mu\text{Sv/h}$ (Moderate) or $\ge 500\text{ }\mu\text{Sv/h}$ (Critical).
- **Explanation**: Deep space solar proton event detected by external vehicle radiation sensors.
- **Mandatory Action**: Evacuate crew to storm shelter core. Verify water-wall shielding. Log cumulative dose.

### D. Hypercapnia (Elevated $\text{CO}_2$)
- **Triggers**:
  - Cabin partial pressure of $\text{CO}_2 \ge 3.5\text{ mmHg}$ (Moderate) or $\ge 5.5\text{ mmHg}$ (Critical).
- **Explanation**: Saturation of amine or LiOH regenerative scrubbing beds.
- **Mandatory Action**: Inspect scrubber manifold, cycle backup ECLSS loop, minimize crew physical exertion.

### E. Sensor Disconnection & Missing Telemetry
- **Triggers**:
  - `sensor_connected == False`.
- **Explanation**: Biometric sensor harness lost skin contact or Bluetooth telemetry dropped.
- **Mandatory Action**: Verify electrode attachment, recharge wearable biosensor, or switch to manual vital entry.
