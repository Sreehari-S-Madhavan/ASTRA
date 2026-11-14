"""
ASTRA: Astronaut Health & Safety Monitoring System
Global Configuration & Constants
"""
import os
import sys
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BASE_DIR.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "astra.db"
REPORTS_DIR = BASE_DIR / "reports"
ASSETS_DIR = BASE_DIR / "assets"
LOGS_DIR = BASE_DIR / "logs"

# Ensure runtime directories exist
for directory in [DATA_DIR, REPORTS_DIR, ASSETS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Application Meta
APP_NAME = "ASTRA"
APP_FULL_NAME = "Astronaut Health & Safety Monitoring System"
APP_VERSION = "1.0.0-PROTOTYPE"
MISSION_NAME = "ARES-V Deep Space Exploration"
HABITAT_LOCATION = "Mars Transit Vehicle (MTV-1) / Lunar Gateway"

# Ground Station Communication Config
GROUND_STATION_HOST = "127.0.0.1"
GROUND_STATION_PORT = 8765
DEFAULT_COMM_DELAY_SECONDS = 3.0  # Simulated light-time delay (configurable)
OFFLINE_MODE = False

# Risk Engine Thresholds (Physiological Baselines)
VITALS_THRESHOLDS = {
    "heart_rate": {"normal_min": 60, "normal_max": 100, "warn_low": 50, "warn_high": 120, "crit_low": 40, "crit_high": 140, "unit": "bpm"},
    "spo2": {"normal_min": 95, "normal_max": 100, "warn_low": 90, "crit_low": 85, "unit": "%"},
    "sys_bp": {"normal_min": 90, "normal_max": 125, "warn_high": 140, "crit_high": 160, "crit_low": 80, "unit": "mmHg"},
    "dia_bp": {"normal_min": 60, "normal_max": 80, "warn_high": 90, "crit_high": 100, "crit_low": 50, "unit": "mmHg"},
    "temperature": {"normal_min": 36.3, "normal_max": 37.5, "warn_high": 38.0, "crit_high": 39.0, "crit_low": 35.0, "unit": "°C"},
    "respiratory_rate": {"normal_min": 12, "normal_max": 20, "warn_high": 24, "crit_high": 30, "crit_low": 8, "unit": "brpm"},
}

ENVIRONMENT_THRESHOLDS = {
    "o2_percent": {"normal_min": 20.5, "normal_max": 23.5, "warn_low": 19.5, "crit_low": 18.0, "crit_high": 25.0, "unit": "%"},
    "co2_mmhg": {"normal_min": 0.0, "normal_max": 3.0, "warn_high": 4.5, "crit_high": 7.0, "unit": "mmHg"},
    "cabin_pressure": {"normal_min": 98.0, "normal_max": 103.0, "warn_low": 94.0, "crit_low": 85.0, "crit_high": 110.0, "unit": "kPa"},
    "cabin_temp": {"normal_min": 20.0, "normal_max": 24.0, "warn_low": 18.0, "warn_high": 26.0, "crit_low": 15.0, "crit_high": 30.0, "unit": "°C"},
    "humidity_pct": {"normal_min": 40.0, "normal_max": 65.0, "warn_low": 30.0, "warn_high": 70.0, "unit": "%"},
    "radiation_rate_usv_h": {"normal_min": 10.0, "normal_max": 50.0, "warn_high": 100.0, "crit_high": 500.0, "unit": "µSv/h"},
}

# Theme Palette (Futuristic Dark Space Station Workstation)
THEME = {
    "bg_dark": "#0A0E17",
    "bg_surface": "#121A2A",
    "bg_card": "#182338",
    "bg_hover": "#22314E",
    "border": "#283958",
    "text_primary": "#F0F4FC",
    "text_secondary": "#94A3B8",
    "text_muted": "#64748B",
    "accent_cyan": "#00E5FF",
    "accent_blue": "#2979FF",
    "accent_glow": "rgba(0, 229, 255, 0.25)",
    "status_normal": "#00E676",
    "status_warning": "#FFB300",
    "status_critical": "#FF1744",
    "status_info": "#00B0FF",
}
