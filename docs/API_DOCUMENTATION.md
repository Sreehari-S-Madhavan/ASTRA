# ASTRA: Ground Station API Documentation

The ASTRA Ground Station service (`astra.physician.server`) provides a lightweight REST API simulating terrestrial Mission Control telemetry receivers and remote Flight Surgeon consoles.

---

## Service Configuration
- **Base Host**: `http://127.0.0.1:8765`
- **Framework**: FastAPI / Starlette
- **Protocols**: HTTP / REST

---

## Endpoints

### 1. Root Status
- **`GET /`**
- **Response**:
```json
{
  "station": "Mission Control Center - Houston (Flight Medicine Console)",
  "status": "ONLINE_STANDBY",
  "active_mission": "ARES-V Deep Space Exploration",
  "timestamp": "2026-11-14T15:30:00.000"
}
```

### 2. Uplink Carrier Health Check
- **`GET /health`**
- **Response**:
```json
{
  "status": "HEALTHY",
  "uplink_carrier": "DEEP_SPACE_NETWORK_70M"
}
```

### 3. Flight Surgeon Directory
- **`GET /api/physicians`**
- **Response**: List of available Flight Surgeons and duty statuses.

### 4. Telemetry Stream Ingestion
- **`POST /api/telemetry`**
- **Body (`application/json`)**:
```json
{
  "spacecraft": "MTV-1 'Chronos'",
  "mission_id": "M-ARES5",
  "astronaut_id": "AST-01",
  "timestamp": "2026-11-14T15:30:00",
  "vitals": {
    "heart_rate": 68.0,
    "spo2": 98.5,
    "sys_bp": 118.0
  },
  "environment": {
    "o2_percent": 21.0,
    "cabin_pressure_kpa": 101.3
  }
}
```
- **Response**: `{"status": "INGESTED", "packet_bytes": 240}`

### 5. Medical Dossier Ingestion
- **`POST /api/reports`**
- **Body (`application/json`)**:
```json
{
  "report_uid": "REP-20261114-A1B2C3",
  "astronaut_id": "AST-01",
  "report_type": "EMERGENCY_INCIDENT_REPORT",
  "severity": "CRITICAL",
  "summary": "Acute decompression event. Crew in storm shelter.",
  "timestamp": "2026-11-14T15:30:00"
}
```
- **Response**: `{"status": "DELIVERED", "report_uid": "REP-20261114-A1B2C3"}`

### 6. Physician Acknowledgement
- **`POST /api/acknowledge/{report_uid}`**
- **Parameters**: `physician_callsign` (query string, default: `MED-LEAD`).
- **Response**:
```json
{
  "status": "ACKNOWLEDGED",
  "report_uid": "REP-20261114-A1B2C3",
  "physician": "MED-LEAD",
  "timestamp": "2026-11-14T15:35:00"
}
```
