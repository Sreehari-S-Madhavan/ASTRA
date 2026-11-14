"""
ASTRA Ground Mission Control Medical Station (FastAPI Server)
Represents the remote terrestrial or lunar base telemetry receiver station.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from astra.database.db_manager import db_manager

app = FastAPI(
    title="ASTRA Ground Flight Surgery Telemetry Station",
    description="Terrestrial Mission Control interface for long-duration deep space mission medical oversight.",
    version="1.0.0"
)


class TelemetryPacket(BaseModel):
    spacecraft: str = "MTV-1 'Chronos'"
    mission_id: str = "M-ARES5"
    astronaut_id: str
    timestamp: str
    vitals: Dict[str, Any]
    environment: Optional[Dict[str, Any]] = None
    alerts: Optional[List[Dict[str, Any]]] = None


class MedicalReportPayload(BaseModel):
    report_uid: str
    astronaut_id: str
    report_type: str
    severity: str
    summary: str
    vitals_snapshot: Optional[Dict[str, Any]] = None
    risk_summary: Optional[Dict[str, Any]] = None
    timestamp: str


@app.get("/")
def read_root():
    return {
        "station": "Mission Control Center - Houston (Flight Medicine Console)",
        "status": "ONLINE_STANDBY",
        "active_mission": "ARES-V Deep Space Exploration",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/health")
def health_check():
    return {"status": "HEALTHY", "uplink_carrier": "DEEP_SPACE_NETWORK_70M"}


@app.get("/api/physicians")
def list_physicians():
    rows = db_manager.execute_query("SELECT * FROM physician_profiles")
    return {"physicians": rows}


@app.post("/api/telemetry")
def ingest_telemetry(packet: TelemetryPacket):
    """Receives in-flight spacecraft telemetry stream."""
    return {
        "status": "INGESTED",
        "received_at": datetime.now().isoformat(),
        "astronaut_id": packet.astronaut_id,
        "packet_bytes": len(packet.model_dump_json())
    }


@app.post("/api/reports")
def receive_report(report: MedicalReportPayload):
    """Receives emergency and routine medical diagnostic reports."""
    now_str = datetime.now().isoformat()
    # Check if report exists
    existing = db_manager.execute_single("SELECT * FROM medical_reports WHERE report_uid = ?", (report.report_uid,))
    if existing:
        db_manager.execute_write(
            "UPDATE medical_reports SET transmission_status = 'DELIVERED' WHERE report_uid = ?",
            (report.report_uid,)
        )
    return {
        "status": "DELIVERED",
        "report_uid": report.report_uid,
        "ground_station_received_at": now_str
    }


@app.post("/api/acknowledge/{report_uid}")
def acknowledge_report(report_uid: str, physician_callsign: str = "MED-LEAD"):
    """Flight surgeon issues signed clinical acknowledgement."""
    now_str = datetime.now().isoformat()
    db_manager.execute_write(
        "UPDATE medical_reports SET transmission_status = 'ACKNOWLEDGED', acknowledged_at = ? WHERE report_uid = ?",
        (now_str, report_uid)
    )
    return {
        "status": "ACKNOWLEDGED",
        "report_uid": report_uid,
        "physician": physician_callsign,
        "timestamp": now_str
    }


def run_ground_server(host: str = "127.0.0.1", port: int = 8765):
    """Starts FastAPI ground station server."""
    uvicorn.run(app, host=host, port=port, log_level="warning")


if __name__ == "__main__":
    run_ground_server()
