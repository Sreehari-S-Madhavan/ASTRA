"""
ASTRA Database Manager
Handles SQLite connection, table schemas, migrations, transactions, and foreign key enforcement.
"""
import sqlite3
import json
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from astra.config import DATABASE_PATH

logger = logging.getLogger("astra.db")

SCHEMA_SQL = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS missions (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    spacecraft TEXT NOT NULL,
    destination TEXT NOT NULL,
    launch_date TEXT NOT NULL,
    duration_days INTEGER NOT NULL,
    current_phase TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE'
);

CREATE TABLE IF NOT EXISTS astronauts (
    id TEXT PRIMARY KEY,
    callsign TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    age INTEGER NOT NULL,
    role TEXT NOT NULL,
    mission_id TEXT NOT NULL,
    baseline_hr REAL DEFAULT 65.0,
    baseline_spo2 REAL DEFAULT 98.0,
    baseline_sys_bp REAL DEFAULT 115.0,
    baseline_dia_bp REAL DEFAULT 75.0,
    baseline_temp REAL DEFAULT 36.6,
    baseline_resp REAL DEFAULT 14.0,
    medical_summary TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (mission_id) REFERENCES missions(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS health_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    heart_rate REAL,
    spo2 REAL,
    sys_bp REAL,
    dia_bp REAL,
    temperature REAL,
    respiratory_rate REAL,
    hydration_index REAL,
    sleep_hours REAL,
    fatigue_score REAL,
    source_type TEXT NOT NULL DEFAULT 'SIMULATED',
    validity_status TEXT NOT NULL DEFAULT 'VALID',
    sensor_connected INTEGER NOT NULL DEFAULT 1,
    notes TEXT,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS symptom_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    category TEXT NOT NULL,
    severity TEXT NOT NULL,
    description TEXT NOT NULL,
    duration_hours REAL DEFAULT 1.0,
    reported_by TEXT NOT NULL,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS camera_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    assessment_type TEXT NOT NULL,
    blink_count INTEGER DEFAULT 0,
    blink_rate_per_min REAL DEFAULT 0.0,
    ear_avg REAL DEFAULT 0.0,
    head_pitch REAL DEFAULT 0.0,
    head_yaw REAL DEFAULT 0.0,
    head_roll REAL DEFAULT 0.0,
    facial_asymmetry_pct REAL DEFAULT 0.0,
    quality_score REAL DEFAULT 100.0,
    tracking_error_px REAL DEFAULT 0.0,
    reaction_time_ms REAL DEFAULT 0.0,
    observation_notes TEXT,
    status TEXT NOT NULL DEFAULT 'COMPLETED',
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS environmental_readings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    o2_percent REAL NOT NULL,
    co2_mmhg REAL NOT NULL,
    cabin_pressure_kpa REAL NOT NULL,
    cabin_temp_c REAL NOT NULL,
    humidity_pct REAL NOT NULL,
    radiation_rate_usv_h REAL NOT NULL,
    system_status TEXT NOT NULL DEFAULT 'NOMINAL',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS hazard_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    hazard_category TEXT NOT NULL,
    severity TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    metric_value REAL NOT NULL,
    threshold_breached TEXT NOT NULL,
    mitigation_action TEXT,
    resolved INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS health_alerts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    alert_level TEXT NOT NULL,
    category TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    triggering_indicators TEXT NOT NULL,
    missing_indicators TEXT,
    recommended_action TEXT NOT NULL,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    acknowledged_by TEXT,
    acknowledged_at TEXT,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS medical_protocols (
    id TEXT PRIMARY KEY,
    code TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    observable_signs TEXT NOT NULL,
    immediate_safety TEXT NOT NULL,
    first_aid_steps TEXT NOT NULL,
    contraindications TEXT NOT NULL,
    escalation_criteria TEXT NOT NULL,
    required_telemetry TEXT NOT NULL,
    approved_by TEXT NOT NULL,
    version TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS emergency_incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    protocol_id TEXT NOT NULL,
    incident_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'ACTIVE',
    initial_vitals TEXT,
    actions_taken TEXT,
    escalation_sent INTEGER DEFAULT 0,
    physician_notified INTEGER DEFAULT 0,
    resolved_at TEXT,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE,
    FOREIGN KEY (protocol_id) REFERENCES medical_protocols(id)
);

CREATE TABLE IF NOT EXISTS physician_profiles (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    callsign TEXT UNIQUE NOT NULL,
    ground_station TEXT NOT NULL,
    email TEXT,
    specialization TEXT NOT NULL,
    availability_status TEXT NOT NULL DEFAULT 'ON_DUTY'
);

CREATE TABLE IF NOT EXISTS medical_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_uid TEXT UNIQUE NOT NULL,
    astronaut_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    report_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    summary TEXT NOT NULL,
    vitals_snapshot TEXT,
    risk_summary TEXT,
    camera_summary TEXT,
    incident_id INTEGER,
    transmission_status TEXT NOT NULL DEFAULT 'DRAFT',
    transmitted_at TEXT,
    acknowledged_at TEXT,
    physician_id TEXT,
    pdf_path TEXT,
    FOREIGN KEY (astronaut_id) REFERENCES astronauts(id) ON DELETE CASCADE,
    FOREIGN KEY (physician_id) REFERENCES physician_profiles(id)
);

CREATE TABLE IF NOT EXISTS communication_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    msg_uid TEXT UNIQUE NOT NULL,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    message_type TEXT NOT NULL,
    priority TEXT NOT NULL DEFAULT 'ROUTINE',
    subject TEXT NOT NULL,
    body TEXT NOT NULL,
    payload_json TEXT,
    simulated_delay_sec REAL DEFAULT 3.0,
    status TEXT NOT NULL DEFAULT 'QUEUED',
    delivered_at TEXT,
    acknowledged_at TEXT
);

CREATE TABLE IF NOT EXISTS system_audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    user_callsign TEXT NOT NULL,
    role TEXT NOT NULL,
    action TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    details TEXT,
    ip_or_station TEXT DEFAULT 'ONBOARD_TERMINAL'
);

CREATE INDEX IF NOT EXISTS idx_health_ast_time ON health_readings(astronaut_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_env_time ON environmental_readings(timestamp);
CREATE INDEX IF NOT EXISTS idx_alerts_ast_time ON health_alerts(astronaut_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_camera_ast_time ON camera_assessments(astronaut_id, timestamp);
CREATE INDEX IF NOT EXISTS idx_comm_status ON communication_messages(status);
"""


class DatabaseManager:
    """Manages SQLite connection lifecycle and schema operations."""
    
    def __init__(self, db_path: Optional[str] = None):
        self.db_path = str(db_path or DATABASE_PATH)
        self.init_database()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_database(self):
        """Execute schema scripts and verify integrity."""
        try:
            with self.get_connection() as conn:
                conn.executescript(SCHEMA_SQL)
                conn.commit()
            logger.info("Database initialized successfully at %s", self.db_path)
        except Exception as e:
            logger.error("Failed to initialize database: %s", e)
            raise

    def execute_write(self, query: str, params: tuple = ()) -> int:
        """Executes INSERT/UPDATE/DELETE and returns lastrowid or rowcount."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid or cursor.rowcount

    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Executes SELECT and returns list of dictionaries."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def execute_single(self, query: str, params: tuple = ()) -> Optional[Dict[str, Any]]:
        """Executes SELECT and returns one dictionary or None."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            return dict(row) if row else None


# Global DB instance
db_manager = DatabaseManager()
