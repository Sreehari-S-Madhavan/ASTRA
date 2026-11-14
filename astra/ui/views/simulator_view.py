"""
ASTRA Mission Simulation Control View (MANDATORY REQUIREMENT 17)
Enables artificial mission scenario injection, manual parameter tuning,
simulation speed scaling, and repeatable test scenario execution.
"""
from typing import Dict, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QComboBox, QSlider, QScrollArea, QMessageBox
)
from PySide6.QtCore import Qt
from astra.config import THEME
from astra.simulation.mission_simulator import simulator, SCENARIOS
from astra.core.event_bus import bus


class SimulatorView(QWidget):
    """Integrated mission simulator control panel."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

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
        t_box = QVBoxLayout()
        title_lbl = QLabel("MISSION TELEMETRY SIMULATOR & SCENARIO INJECTOR")
        title_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 13px; letter-spacing: 1px;")
        t_box.addWidget(title_lbl)
        sub_lbl = QLabel("Mandatory test environment for simulating acute physiological distress, ECLSS life support faults, and space hazards.")
        sub_lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 11px;")
        t_box.addWidget(sub_lbl)
        layout.addLayout(t_box)

        # Scenario Selection Card
        sc_frame = QFrame()
        sc_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        sc_layout = QVBoxLayout(sc_frame)
        sc_layout.setSpacing(8)

        sc_title = QLabel("SELECT PREDEFINED MISSION ANOMALY SCENARIO:")
        sc_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        sc_layout.addWidget(sc_title)

        c_row = QHBoxLayout()
        self.combo_scenarios = QComboBox()
        for key, sc in SCENARIOS.items():
            self.combo_scenarios.addItem(f"{sc['name']} [{key}]", key)
        c_row.addWidget(self.combo_scenarios, stretch=3)

        btn_load = QPushButton("INJECT SCENARIO TELEMETRY")
        btn_load.setObjectName("primaryBtn")
        btn_load.clicked.connect(self._load_selected_scenario)
        c_row.addWidget(btn_load, stretch=1)
        sc_layout.addLayout(c_row)

        self.lbl_sc_desc = QLabel(SCENARIOS["NOMINAL"]["description"])
        self.lbl_sc_desc.setStyleSheet(f"color: {THEME['text_secondary']}; font-style: italic; padding: 4px;")
        self.lbl_sc_desc.setWordWrap(True)
        sc_layout.addWidget(self.lbl_sc_desc)
        self.combo_scenarios.currentIndexChanged.connect(self._on_scenario_selected)

        # Simulator Speed & Execution Controls
        ctrl_row = QHBoxLayout()
        self.btn_toggle_sim = QPushButton("PAUSE SIMULATOR ENGINE" if simulator.is_running else "RESUME SIMULATOR ENGINE")
        self.btn_toggle_sim.clicked.connect(self._toggle_sim)
        ctrl_row.addWidget(self.btn_toggle_sim)

        ctrl_row.addWidget(QLabel("Simulation Speed Multiplier:"))
        self.combo_speed = QComboBox()
        self.combo_speed.addItems(["0.5x Real-Time", "1.0x Real-Time", "2.0x Scaled", "5.0x Accelerated", "10.0x Warp"])
        self.combo_speed.setCurrentIndex(1)
        self.combo_speed.currentIndexChanged.connect(self._on_speed_changed)
        ctrl_row.addWidget(self.combo_speed)

        ctrl_row.addStretch()
        btn_reset = QPushButton("RESET ALL TO NOMINAL BASELINE")
        btn_reset.clicked.connect(lambda: self._load_scenario_by_key("NOMINAL"))
        ctrl_row.addWidget(btn_reset)

        sc_layout.addLayout(ctrl_row)
        layout.addWidget(sc_frame)

        # Manual Parameter Tuning Sliders Grid
        man_frame = QFrame()
        man_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 8px; padding: 12px;")
        mf_layout = QVBoxLayout(man_frame)
        mf_title = QLabel("MANUAL TELEMETRY PARAMETER INJECTION & FINE-TUNING:")
        mf_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        mf_layout.addWidget(mf_title)

        grid = QGridLayout()
        grid.setSpacing(12)

        # Row 1: Vitals
        self.slider_hr, self.lbl_val_hr = self._add_slider_row(grid, 0, "Heart Rate (bpm):", 40, 180, 68, lambda v: simulator.set_manual_vital("heart_rate", float(v)))
        self.slider_spo2, self.lbl_val_spo2 = self._add_slider_row(grid, 1, "SpO2 Saturation (%):", 75, 100, 98, lambda v: simulator.set_manual_vital("spo2", float(v)))
        self.slider_bp, self.lbl_val_bp = self._add_slider_row(grid, 2, "Systolic BP (mmHg):", 70, 180, 118, lambda v: simulator.set_manual_vital("sys_bp", float(v)))
        self.slider_temp, self.lbl_val_temp = self._add_slider_row(grid, 3, "Core Temp (°C x 10):", 340, 410, 366, lambda v: simulator.set_manual_vital("temperature", float(v) / 10.0))

        # Row 2: Environment
        self.slider_o2, self.lbl_val_o2 = self._add_slider_row(grid, 4, "Cabin O2 (% x 10):", 140, 250, 210, lambda v: simulator.set_manual_env("o2_percent", float(v) / 10.0))
        self.slider_co2, self.lbl_val_co2 = self._add_slider_row(grid, 5, "Cabin CO2 (mmHg x 10):", 0, 80, 18, lambda v: simulator.set_manual_env("co2_mmhg", float(v) / 10.0))
        self.slider_press, self.lbl_val_press = self._add_slider_row(grid, 6, "Pressure (kPa):", 75, 110, 101, lambda v: simulator.set_manual_env("cabin_pressure_kpa", float(v)))
        self.slider_rad, self.lbl_val_rad = self._add_slider_row(grid, 7, "Radiation Rate (µSv/h):", 5, 600, 25, lambda v: simulator.set_manual_env("radiation_rate_usv_h", float(v)))

        mf_layout.addLayout(grid)
        layout.addWidget(man_frame)

        scroll.setWidget(content_widget)
        main_layout.addWidget(scroll)

    def _add_slider_row(self, grid: QGridLayout, row: int, label: str, min_v: int, max_v: int, init_v: int, callback):
        lbl = QLabel(label)
        lbl.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 10px;")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(min_v, max_v)
        slider.setValue(init_v)

        val_lbl = QLabel(f"{init_v}")
        val_lbl.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 11px; min-width: 35px;")

        def on_change(val):
            val_lbl.setText(f"{val/10.0:.1f}" if "x 10" in label else f"{val}")
            callback(val)

        slider.valueChanged.connect(on_change)
        grid.addWidget(lbl, row, 0)
        grid.addWidget(slider, row, 1)
        grid.addWidget(val_lbl, row, 2)
        return slider, val_lbl

    def _on_scenario_selected(self, idx: int):
        key = self.combo_scenarios.currentData()
        if key in SCENARIOS:
            self.lbl_sc_desc.setText(SCENARIOS[key]["description"])

    def _load_selected_scenario(self):
        key = self.combo_scenarios.currentData()
        self._load_scenario_by_key(key)

    def _load_scenario_by_key(self, key: str):
        simulator.load_scenario(key)
        sc = SCENARIOS.get(key, {})
        QMessageBox.information(self, "Scenario Injected", f"Simulation scenario '{sc.get('name')}' active.\nTelemetry stream will reflect anomaly conditions.")
        bus.companion_message_requested.emit(f"Simulation scenario injected: {sc.get('name')}. Telemetry loops shifting to anomaly parameters.", "concerned" if key != "NOMINAL" else "happy")

    def _toggle_sim(self):
        if simulator.is_running:
            simulator.stop()
            self.btn_toggle_sim.setText("RESUME SIMULATOR ENGINE")
        else:
            simulator.start()
            self.btn_toggle_sim.setText("PAUSE SIMULATOR ENGINE")

    def _on_speed_changed(self, idx: int):
        speeds = [0.5, 1.0, 2.0, 5.0, 10.0]
        simulator.set_speed(speeds[idx])
