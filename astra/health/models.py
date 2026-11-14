"""
ASTRA Health Models
Structured dataclasses for physiological vitals, environmental telemetry,
camera screening observations, symptoms, and health alerts.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any
from datetime import datetime


@dataclass
class VitalSigns:
    astronaut_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    heart_rate: Optional[float] = 70.0
    spo2: Optional[float] = 98.0
    sys_bp: Optional[float] = 118.0
    dia_bp: Optional[float] = 76.0
    temperature: Optional[float] = 36.6
    respiratory_rate: Optional[float] = 14.0
    hydration_index: Optional[float] = 90.0
    sleep_hours: Optional[float] = 7.5
    fatigue_score: Optional[float] = 2.0  # 1-10 scale (1 = refreshed, 10 = exhausted)
    source_type: str = "SIMULATED"        # 'SIMULATED' or 'SENSOR'
    validity_status: str = "VALID"       # 'VALID', 'DEGRADED', 'INVALID'
    sensor_connected: bool = True
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class EnvironmentalMetrics:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    o2_percent: float = 21.0
    co2_mmhg: float = 1.8
    cabin_pressure_kpa: float = 101.3
    cabin_temp_c: float = 22.0
    humidity_pct: float = 48.0
    radiation_rate_usv_h: float = 25.0
    system_status: str = "NOMINAL"
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CameraObservation:
    astronaut_id: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    assessment_type: str = "ROUTINE_SCREENING"  # ROUTINE_SCREENING, EYE_TRACKING, REACTION_TIME, POSTURE
    blink_count: int = 0
    blink_rate_per_min: float = 0.0
    ear_avg: float = 0.30
    head_pitch: float = 0.0
    head_yaw: float = 0.0
    head_roll: float = 0.0
    facial_asymmetry_pct: float = 0.0
    quality_score: float = 100.0
    tracking_error_px: float = 0.0
    reaction_time_ms: float = 0.0
    observation_notes: str = ""
    status: str = "COMPLETED"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class HealthAlert:
    astronaut_id: str
    alert_level: str  # LOW, MODERATE, CRITICAL
    category: str    # Cardiovascular, Respiratory, Hypoxia, Radiation, etc.
    title: str
    description: str
    triggering_indicators: List[str]
    recommended_action: str
    missing_indicators: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    acknowledged: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
