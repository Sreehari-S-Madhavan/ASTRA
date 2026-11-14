# ASTRA: Mission Simulation Guide

## 1. Overview
The **ASTRA Mission Simulation Engine** (`astra.simulation.mission_simulator`) is a mandatory subsystem allowing developers, medical researchers, and astronauts to test and evaluate health screening, hazard triggers, and emergency life-support workflows under controlled, reproducible conditions.

## 2. Predefined Simulation Scenarios

| Scenario Key | Title & Context | Telemetry Signatures | Triggered Alerts |
| :--- | :--- | :--- | :--- |
| `NOMINAL` | Routine Deep Space Operations | HR: 68 bpm, SpO2: 98.5%, O2: 21%, Press: 101.3 kPa | None (Green Status) |
| `ELEVATED_HR` | Severe Tachycardia / Arrhythmia | HR: 136 bpm, Sys BP: 142 mmHg, Resp: 24 | Moderate Cardiovascular Warning |
| `HYPOXIA` | Cabin Depressurization & O2 Drop | SpO2: 84%, Cabin O2: 16.5%, Pressure: 86 kPa | Critical Hypoxia / Decompression |
| `HYPERCAPNIA` | ECLSS CO2 Scrubber Fault | CO2: 5.4 mmHg, Resp: 22, SpO2: 95% | Critical CO2 Toxicity Alert |
| `RADIATION_STORM` | Solar Particle Event (SPE) | Radiation Flux: 420 µSv/h | Critical Solar Radiation Storm |
| `DEHYDRATION` | Severe Dehydration & Heat Strain | HR: 125 bpm, Temp: 38.7°C, Hydration: 64% | Critical Pyrexia / Dehydration |
| `SENSOR_DISCONNECT` | Biometric Lead Disconnection | HR: None, SpO2: None, `sensor_connected`: False | Sensor Integrity Alert |
| `COMM_FAILURE` | Solar Conjunction Comm Blackout | DSN Latency: 1200s (20m), Offline Mode: True | Deep Space Autonomy Alert |

## 3. Manual Parameter Sliders
The simulation view provides interactive sliders for real-time fine tuning:
- **Heart Rate**: 40 to 180 bpm.
- **SpO2**: 75 to 100%.
- **Systolic BP**: 70 to 180 mmHg.
- **Core Body Temp**: 34.0 to 41.0 °C.
- **Cabin O2**: 14.0 to 25.0%.
- **Cabin CO2**: 0.0 to 8.0 mmHg.
- **Cabin Pressure**: 75.0 to 110.0 kPa.
- **Radiation Flux**: 5 to 600 µSv/h.

## 4. Execution Controls & Time Scaling
- **Speed Multipliers**: `0.5x`, `1.0x` (Real-Time), `2.0x`, `5.0x`, and `10.0x` (Fast-Forward).
- **Telemetry Noise**: Every second, realistic Gaussian biometric variation is applied to simulate biological signal fluctuation.
- **Database Persistence**: Simulated readings are automatically persisted to the SQLite database every 10 ticks.
