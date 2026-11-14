"""
ASTRA Spaceflight Hazards Monitoring View
Dedicated operational console for monitoring the five primary spaceflight hazards:
1. Space Radiation
2. Isolation & Confinement
3. Distance from Earth
4. Gravity Fields
5. Hostile / Closed Environments (ECLSS)
"""
from typing import Dict, Any, List
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QProgressBar, QSlider, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.ui.widgets.metric_card import MetricCard
from astra.health.hazard_engine import hazard_engine
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager


class HazardsMonitoringView(QWidget):
    """Monitors the 5 major spaceflight hazards with interactive mitigation controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.cached_env: Dict[str, Any] = {}
        self.cached_vitals: Dict[str, Any] = {}
        self._setup_ui()

        # Connect to event bus
        bus.environment_updated.connect(self.on_env_updated)
        bus.vitals_updated.connect(self.on_vitals_updated)

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(14)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        # Header Title
        title_lbl = QLabel("FIVE SPACEFLIGHT HAZARDS OPERATIONAL CONSOLE")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        layout.addWidget(title_lbl)

        # HAZARD 1: Space Radiation
        rad_frame = self._create_card("HAZARD 1 • SPACE RADIATION (GALACTIC COSMIC RAYS & SOLAR EVENTS)")
        rf_layout = QVBoxLayout(rad_frame)
        rf_grid = QHBoxLayout()
        self.card_rad_flux = MetricCard("Radiation Flux", "µSv/h", 10.0, 50.0)
        self.card_rad_cumul = MetricCard("Cumulative Mission Dose", "mSv", 0.0, 250.0)
        self.card_rad_cumul.set_value(48.5, "NOMINAL")
        rf_grid.addWidget(self.card_rad_flux)
        rf_grid.addWidget(self.card_rad_cumul)
        rf_layout.addLayout(rf_grid)

        btn_shelter = QPushButton("ACTIVATE STORM SHELTER PROTOCOL")
        btn_shelter.clicked.connect(lambda: self._trigger_hazard_mitigation("RADIATION", "Crew directed to central storm shelter core with polyethylene/water shielding."))
        rf_layout.addWidget(btn_shelter)
        layout.addWidget(rad_frame)

        # HAZARD 2: Isolation & Confinement
        iso_frame = self._create_card("HAZARD 2 • ISOLATION & CONFINEMENT (CIRCADIAN DISRUPTION & FATIGUE)")
        if_layout = QVBoxLayout(iso_frame)
        if_grid = QHBoxLayout()
        self.card_sleep = MetricCard("Last Sleep Block", "hours", 6.5, 9.0)
        self.card_fatigue = MetricCard("Subjective Fatigue", "/10", 0.0, 5.0)
        self.card_sleep.set_value(7.5, "NOMINAL")
        self.card_fatigue.set_value(2.0, "NOMINAL")
        if_grid.addWidget(self.card_sleep)
        if_grid.addWidget(self.card_fatigue)
        if_layout.addLayout(if_grid)

        btn_circadian = QPushButton("INITIATE BLUE-DEPLETED CIRCADIAN RELAXATION CYCLE")
        btn_circadian.clicked.connect(lambda: self._trigger_hazard_mitigation("ISOLATION", "Habitat lighting shifted to 2200K amber relaxation mode. Audio white noise engaged."))
        if_layout.addWidget(btn_circadian)
        layout.addWidget(iso_frame)

        # HAZARD 3: Distance from Earth
        dist_frame = self._create_card("HAZARD 3 • DISTANCE FROM EARTH (LIGHT-TIME LATENCY & AUTONOMY)")
        df_layout = QVBoxLayout(dist_frame)
        df_info = QHBoxLayout()
        self.lbl_latency = QLabel("SIMULATED ONE-WAY PROPAGATION DELAY: 3.0 SECONDS (ORBITAL TEST)")
        self.lbl_latency.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        df_info.addWidget(self.lbl_latency)
        df_info.addStretch()

        self.btn_offline = QPushButton("TOGGLE OFFLINE AUTONOMY MODE")
        self.btn_offline.setCheckable(True)
        self.btn_offline.clicked.connect(self._toggle_offline_mode)
        df_info.addWidget(self.btn_offline)
        df_layout.addLayout(df_info)

        # Latency Slider
        slider_box = QHBoxLayout()
        slider_box.addWidget(QLabel("Latency Delay:"))
        self.slider_delay = QSlider(Qt.Horizontal)
        self.slider_delay.setRange(0, 1200) # 0 to 20 minutes
        self.slider_delay.setValue(3)
        self.slider_delay.valueChanged.connect(self._on_latency_changed)
        slider_box.addWidget(self.slider_delay)
        df_layout.addLayout(slider_box)
        layout.addWidget(dist_frame)

        # HAZARD 4: Gravity Fields / Microgravity
        grav_frame = self._create_card("HAZARD 4 • GRAVITY FIELDS (VESTIBULAR ADAPTATION, MOTOR SACCADES & SANS)")
        gf_layout = QVBoxLayout(grav_frame)
        gf_grid = QHBoxLayout()
        self.card_saccade = MetricCard("Smooth Pursuit Saccade Error", "px", 0.0, 25.0)
        self.card_coordination = MetricCard("Vestibular Coordination", "%", 80.0, 100.0)
        self.card_saccade.set_value(12.0, "NOMINAL")
        self.card_coordination.set_value(94.0, "NOMINAL")
        gf_grid.addWidget(self.card_saccade)
        gf_grid.addWidget(self.card_coordination)
        gf_layout.addLayout(gf_grid)

        btn_vestibular = QPushButton("INITIATE 15-MIN VESTIBULAR RECALIBRATION DRILL")
        btn_vestibular.clicked.connect(lambda: self._trigger_hazard_mitigation("GRAVITY", "Vestibular adaptation head stabilization protocol active."))
        gf_layout.addWidget(btn_vestibular)
        layout.addWidget(grav_frame)

        # HAZARD 5: Hostile & Closed Environments (ECLSS)
        eclss_frame = self._create_card("HAZARD 5 • HOSTILE & CLOSED ENVIRONMENTS (CABIN ATMOSPHERE INTEGRITY)")
        ef_layout = QVBoxLayout(eclss_frame)
        ef_grid = QHBoxLayout()
        self.card_o2 = MetricCard("Cabin O2", "%", 20.5, 23.5)
        self.card_co2 = MetricCard("Cabin CO2", "mmHg", 0.0, 3.0)
        self.card_press = MetricCard("Pressure", "kPa", 98.0, 103.0)
        ef_grid.addWidget(self.card_o2)
        ef_grid.addWidget(self.card_co2)
        ef_grid.addWidget(self.card_press)
        ef_layout.addLayout(ef_grid)

        btn_eclss = QPushButton("PURGE & CYCLE ECLSS CO2 AMINE SCRUBBERS")
        btn_eclss.clicked.connect(lambda: self._trigger_hazard_mitigation("ECLSS", "Backup regenerative amine bed cycled. CO2 purge manifold open."))
        ef_layout.addWidget(btn_eclss)
        layout.addWidget(eclss_frame)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _create_card(self, title: str) -> QFrame:
        f = QFrame()
        f.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 10px;")
        t_lbl = QLabel(title)
        t_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 11px;")
        f.layout = QVBoxLayout(f)
        f.layout.addWidget(t_lbl)
        return f

    def on_env_updated(self, env: Dict[str, Any]):
        self.cached_env = env
        rad = env.get("radiation_rate_usv_h", 25.0)
        o2 = env.get("o2_percent", 21.0)
        co2 = env.get("co2_mmhg", 1.8)
        press = env.get("cabin_pressure_kpa", 101.3)

        self.card_rad_flux.set_value(rad, "CRITICAL" if rad > 300 else ("WARNING" if rad > 100 else "NOMINAL"))
        self.card_o2.set_value(o2, "CRITICAL" if o2 < 18 else ("WARNING" if o2 < 19.5 else "NOMINAL"))
        self.card_co2.set_value(co2, "CRITICAL" if co2 > 5.5 else ("WARNING" if co2 > 3.5 else "NOMINAL"))
        self.card_press.set_value(press, "CRITICAL" if press < 90 else ("WARNING" if press < 95 else "NOMINAL"))

    def on_vitals_updated(self, vitals: Dict[str, Any]):
        self.cached_vitals = vitals
        sleep = vitals.get("sleep_hours")
        fatigue = vitals.get("fatigue_score")
        if sleep is not None:
            self.card_sleep.set_value(sleep, "WARNING" if sleep < 5.0 else "NOMINAL")
        if fatigue is not None:
            self.card_fatigue.set_value(fatigue, "WARNING" if fatigue >= 7.0 else "NOMINAL")

    def _on_latency_changed(self, val: int):
        from astra.physician.comm_manager import comm_manager
        comm_manager.set_comm_delay(float(val))
        if val >= 60:
            txt = f"{val/60.0:.1f} MINUTES (DEEP SPACE MARS TRANSIT)"
        else:
            txt = f"{val:.1f} SECONDS (LUNAR / LOW ORBIT)"
        self.lbl_latency.setText(f"SIMULATED ONE-WAY PROPAGATION DELAY: {txt}")

    def _toggle_offline_mode(self):
        from astra.physician.comm_manager import comm_manager
        is_off = self.btn_offline.isChecked()
        comm_manager.set_offline_mode(is_off)
        if is_off:
            self.btn_offline.setText("AUTONOMY MODE ACTIVE (OFFLINE)")
            self.btn_offline.setStyleSheet(f"background-color: {THEME['status_warning']}; color: black; font-weight: bold;")
            bus.companion_message_requested.emit("Spacecraft entering deep space communication blackout. Autonomous medical diagnostics engaged.", "concerned")
        else:
            self.btn_offline.setText("TOGGLE OFFLINE AUTONOMY MODE")
            self.btn_offline.setStyleSheet("")
            bus.companion_message_requested.emit("Uplink restored. Queued telemetry packets synchronizing with ground station.", "happy")

    def _trigger_hazard_mitigation(self, hazard: str, action_details: str):
        QMessageBox.information(self, f"Mitigation Action: {hazard}", f"Action executed successfully:\n\n{action_details}")
        bus.companion_message_requested.emit(f"Mitigation protocol executed for {hazard}. Sensors monitoring recovery.", "thinking")
