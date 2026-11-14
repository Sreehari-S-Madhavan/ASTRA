"""
ASTRA Camera-Based Visual Health Screening View (PRIMARY PRIORITY)
Live computer vision interface integrating face detection, eye tracking, blink rate (EAR),
head pose estimation (solvePnP), camera quality metrics, guided visual tracking tests,
visual reaction time tests, and posture assessments.
"""
from typing import Dict, Any, Optional
import time
import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QCheckBox, QComboBox, QTableWidget, QTableWidgetItem, QProgressBar, QMessageBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from astra.config import THEME
from astra.cv.camera_manager import CameraThread
from astra.cv.vision_engine import vision_engine
from astra.cv.visual_tests import tracking_test, reaction_test, coordination_test
from astra.ui.widgets.camera_view_widget import CameraViewportWidget
from astra.core.event_bus import bus
from astra.database.db_manager import db_manager
from astra.core.audit import log_audit


class CameraScreeningView(QWidget):
    """Central interactive computer vision screening workstation."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.active_astronaut_id = "AST-01"
        self.camera_thread = CameraThread(device_index=0)
        self.current_cv_results: Dict[str, Any] = {}
        self.current_quality: Dict[str, Any] = {}

        self._setup_ui()
        self._connect_signals()

        # Start camera thread
        self.camera_thread.start()

    def _setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)

        # LEFT COLUMN: Live Camera Viewport & Quality HUD
        left_box = QVBoxLayout()
        left_box.setSpacing(10)

        # Viewport Frame
        vp_frame = QFrame()
        vp_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {THEME['bg_surface']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
            }}
        """)
        vp_layout = QVBoxLayout(vp_frame)
        vp_layout.setContentsMargins(6, 6, 6, 6)
        self.viewport = CameraViewportWidget()
        vp_layout.addWidget(self.viewport)
        left_box.addWidget(vp_frame, stretch=4)

        # Quality & Camera Status HUD
        quality_frame = QFrame()
        quality_frame.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 6px; padding: 6px;")
        q_layout = QHBoxLayout(quality_frame)
        q_layout.setContentsMargins(10, 4, 10, 4)

        self.lbl_cam_status = QLabel("CAM: CONNECTED (640x480)")
        self.lbl_cam_status.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 10px;")
        q_layout.addWidget(self.lbl_cam_status)

        self.lbl_cam_quality = QLabel("QUALITY: 95% (EXCELLENT)")
        self.lbl_cam_quality.setStyleSheet(f"color: {THEME['status_normal']}; font-weight: bold; font-size: 10px;")
        q_layout.addWidget(self.lbl_cam_quality)

        self.lbl_cam_illum = QLabel("ILLUM: 125 LUX")
        self.lbl_cam_illum.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 10px;")
        q_layout.addWidget(self.lbl_cam_illum)

        self.btn_synth_toggle = QPushButton("SWITCH TO TEST FEED")
        self.btn_synth_toggle.setStyleSheet("font-size: 9px; padding: 2px 6px;")
        self.btn_synth_toggle.clicked.connect(self.camera_thread.toggle_synthetic)
        q_layout.addWidget(self.btn_synth_toggle)

        left_box.addWidget(quality_frame)

        camera_options = QHBoxLayout()
        camera_options.addWidget(QLabel("CAMERA ROTATION"))
        self.cmb_camera_rotation = QComboBox()
        self.cmb_camera_rotation.addItem("0°", 0)
        self.cmb_camera_rotation.addItem("90° clockwise", -1)
        self.cmb_camera_rotation.addItem("180°", 2)
        self.cmb_camera_rotation.addItem("90° counter-clockwise", 1)
        camera_options.addWidget(self.cmb_camera_rotation)
        self.cb_mirror = QCheckBox("Mirror selfie view")
        self.cb_mirror.setChecked(True)
        camera_options.addWidget(self.cb_mirror)
        camera_options.addStretch()
        left_box.addLayout(camera_options)

        # Medical Disclaimer Pill
        disc_lbl = QLabel(
            "MEDICAL NOTICE: Optical camera screenings provide visual observations and functional reaction metrics only. "
            "They do not constitute diagnostic medical evaluations or cardiovascular disease confirmations."
        )
        disc_lbl.setWordWrap(True)
        disc_lbl.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 9px; line-height: 12px;")
        left_box.addWidget(disc_lbl)

        main_layout.addLayout(left_box, stretch=3)

        # RIGHT COLUMN: Telemetry Readouts, Test Controls, and History
        right_box = QVBoxLayout()
        right_box.setSpacing(12)

        # Section Header
        hdr_lbl = QLabel("VISUAL SCREENING METRICS & GUIDED TESTS")
        hdr_lbl.setStyleSheet(f"color: {THEME['accent_cyan']}; font-weight: bold; font-size: 12px; letter-spacing: 0.5px;")
        right_box.addWidget(hdr_lbl)

        # Real-time Metrics Table
        self.metrics_table = QTableWidget(6, 2)
        self.metrics_table.setHorizontalHeaderLabels(["Diagnostic Parameter", "Real-Time Value"])
        self.metrics_table.horizontalHeader().setStretchLastSection(True)
        self.metrics_table.verticalHeader().setVisible(False)
        self.metrics_table.setSelectionMode(QTableWidget.NoSelection)
        self.metrics_table.setFixedHeight(185)

        params = [
            ("Face Detection Lock", "SEARCHING..."),
            ("Blink Count (Session)", "0 blinks"),
            ("Rolling Blink Frequency", "--"),
            ("Eye Aspect Ratio (EAR)", "--"),
            ("Head Pose (Pitch, Yaw, Roll)", "--"),
            ("Facial Symmetry Score", "--")
        ]
        for row, (p_name, p_val) in enumerate(params):
            i_name = QTableWidgetItem(p_name)
            i_val = QTableWidgetItem(p_val)
            i_name.setForeground(Qt.white)
            i_val.setForeground(Qt.cyan)
            self.metrics_table.setItem(row, 0, i_name)
            self.metrics_table.setItem(row, 1, i_val)

        right_box.addWidget(self.metrics_table)

        # Interactive Test Controls Panel
        test_panel = QFrame()
        test_panel.setStyleSheet(f"background-color: {THEME['bg_surface']}; border: 1px solid {THEME['border']}; border-radius: 6px; padding: 10px;")
        tp_layout = QVBoxLayout(test_panel)
        tp_layout.setSpacing(8)

        tp_title = QLabel("GUIDED NEURO-VESTIBULAR & VISUAL TESTS")
        tp_title.setStyleSheet(f"color: {THEME['text_primary']}; font-weight: bold; font-size: 11px;")
        tp_layout.addWidget(tp_title)

        # Test 1: Guided Eye Tracking
        self.btn_tracking = QPushButton("1. START GUIDED EYE-TRACKING (SMOOTH PURSUIT)")
        self.btn_tracking.clicked.connect(self._toggle_tracking_test)
        tp_layout.addWidget(self.btn_tracking)

        # Test 2: Reaction Time
        self.btn_reaction = QPushButton("2. START VISUAL REACTION-TIME TEST")
        self.btn_reaction.clicked.connect(self._toggle_reaction_test)
        tp_layout.addWidget(self.btn_reaction)

        # Test 3: Guided Coordination
        self.btn_coordination = QPushButton("3. START GUIDED HEAD-COORDINATION TEST")
        self.btn_coordination.clicked.connect(self._toggle_coordination_test)
        tp_layout.addWidget(self.btn_coordination)

        # Checkboxes for HUD overlays
        cb_layout = QHBoxLayout()
        self.cb_overlays = QCheckBox("Show Landmarks & Pose Axes")
        self.cb_overlays.setChecked(True)
        cb_layout.addWidget(self.cb_overlays)

        self.cb_rppg = QCheckBox("Experimental Camera Pulse (rPPG)")
        self.cb_rppg.setChecked(False)
        cb_layout.addWidget(self.cb_rppg)
        tp_layout.addLayout(cb_layout)

        right_box.addWidget(test_panel)

        # Session Action Buttons
        act_layout = QHBoxLayout()
        self.btn_record = QPushButton("LOG SCREENING TO MEDICAL RECORD")
        self.btn_record.setObjectName("primaryBtn")
        self.btn_record.clicked.connect(self._record_session)
        act_layout.addWidget(self.btn_record)

        self.btn_reset = QPushButton("RESET COUNTERS")
        self.btn_reset.clicked.connect(vision_engine.reset_screening_stats)
        act_layout.addWidget(self.btn_reset)
        right_box.addLayout(act_layout)

        right_box.addStretch()
        main_layout.addLayout(right_box, stretch=2)

    def _connect_signals(self):
        self.camera_thread.frame_ready.connect(self._on_frame_ready)
        self.camera_thread.camera_status_changed.connect(self._on_cam_status)
        tracking_test.test_completed.connect(self._on_test_completed)
        reaction_test.test_completed.connect(self._on_test_completed)
        coordination_test.test_completed.connect(self._on_test_completed)

    def _on_cam_status(self, status: str, message: str):
        synthetic = self.camera_thread.use_synthetic_feed or "SYNTHETIC" in status or "Procedural Synthetic" in message
        self.lbl_cam_status.setText(f"CAM: {'SYNTHETIC DEMO' if synthetic else status}")
        if synthetic:
            self.btn_synth_toggle.setText("SWITCH TO PHYSICAL WEBCAM")
        else:
            self.btn_synth_toggle.setText("SWITCH TO TEST FEED")

    def _on_frame_ready(self, frame, quality: dict):
        rotation = self.cmb_camera_rotation.currentData()
        if rotation:
            frame = np.rot90(frame, k=rotation)
        if self.cb_mirror.isChecked():
            frame = np.flip(frame, axis=1)
        frame = np.ascontiguousarray(frame)

        self.current_quality = quality
        self.lbl_cam_quality.setText(f"QUALITY: {quality.get('quality_score', 90):.0f}% ({quality.get('status', 'OK')})")
        self.lbl_cam_illum.setText(f"ILLUM: {quality.get('brightness', 120):.0f}")

        # Process frame via Computer Vision Engine
        processed_frame, results = vision_engine.process_frame(
            frame,
            draw_overlays=self.cb_overlays.isChecked(),
            enable_rppg=self.cb_rppg.isChecked()
        )
        self.current_cv_results = results

        h, w = frame.shape[:2]
        scan_status = self._scan_guidance(results, w, h, quality)
        self.viewport.set_scan_status(scan_status, scan_status == "FACE LOCKED - HOLD STILL")

        # Update Guided Tests
        if tracking_test.is_active:
            target_pt = tracking_test.get_target_position(w, h)
            self.viewport.set_tracking_target(target_pt)
            pitch, yaw = results.get("head_pitch"), results.get("head_yaw")
            if results.get("face_detected") and pitch is not None and yaw is not None:
                face_center = (int(w / 2 + yaw * 4), int(h / 2 + pitch * 4))
                tracking_test.record_sample(target_pt, face_center)
        else:
            self.viewport.set_tracking_target(None)

        if reaction_test.is_waiting_stimulus or reaction_test.stimulus_active:
            stim_active = reaction_test.update()
            self.viewport.set_reaction_stimulus(stim_active)
        else:
            self.viewport.set_reaction_stimulus(False)

        if coordination_test.is_active:
            pitch, yaw = results.get("head_pitch"), results.get("head_yaw")
            if results.get("face_detected") and pitch is not None and yaw is not None:
                st = coordination_test.update(pitch, yaw)
                if st.get("active"):
                    self.viewport.set_coordination_prompt(f"STAGE {st['stage_index']}/{st['total_stages']}: {st['stage_name']}")
                else:
                    self.viewport.set_coordination_prompt("")
            else:
                coordination_test.stage_start_time = time.time()
                self.viewport.set_coordination_prompt("FACE LOST - RETURN TO THE GUIDE")
        else:
            self.viewport.set_coordination_prompt("")

        # Render processed frame in viewport
        self.viewport.update_frame(processed_frame)

        # Update telemetry table
        self._update_table(results)

    @staticmethod
    def _scan_guidance(results: dict, frame_width: int, frame_height: int, quality: dict) -> str:
        quality_status = quality.get("status")
        if quality_status in {"LOW_LIGHT", "OVEREXPOSED", "BLURRY"}:
            return {
                "LOW_LIGHT": "ADD LIGHT TO YOUR FACE",
                "OVEREXPOSED": "REDUCE LIGHT ON YOUR FACE",
                "BLURRY": "HOLD STILL AND CLEAN THE LENS",
            }[quality_status]

        if results.get("analysis_status") == "DETECTION_UNAVAILABLE":
            return "FACE DETECTOR UNAVAILABLE"
        if quality_status == "LOW_QUALITY":
            return "IMPROVE CAMERA LIGHTING AND FOCUS"
        if not results.get("face_detected"):
            return "CENTER YOUR FACE INSIDE THE OVAL"

        face_box = results.get("face_bbox")
        if not face_box:
            return "FACE LOCKED - HOLD STILL"

        x, y, width, height = face_box
        center_x = (x + width / 2) / frame_width
        center_y = (y + height / 2) / frame_height
        width_ratio = width / frame_width
        if width_ratio < 0.20:
            return "MOVE CLOSER TO THE CAMERA"
        if width_ratio > 0.68:
            return "MOVE BACK FROM THE CAMERA"
        if not 0.35 <= center_x <= 0.65 or not 0.25 <= center_y <= 0.75:
            return "CENTER YOUR FACE INSIDE THE OVAL"
        return "FACE LOCKED - HOLD STILL"

    def _update_table(self, res: dict):
        lock_str = "LOCKED [CREW PRIMARY]" if res.get("face_detected") else "SEARCHING..."
        self.metrics_table.item(0, 1).setText(lock_str)
        self.metrics_table.item(0, 1).setForeground(Qt.green if res.get("face_detected") else Qt.red)

        self.metrics_table.item(1, 1).setText(f"{res.get('blink_count', 0)} blinks")
        blink_rate = res.get("blink_rate_per_min")
        self.metrics_table.item(2, 1).setText(f"{blink_rate:.1f} / min" if blink_rate is not None else "--")
        ear = res.get("ear")
        self.metrics_table.item(3, 1).setText(f"{ear:.3f}" if ear is not None else "--")

        pose_values = (res.get("head_pitch"), res.get("head_yaw"), res.get("head_roll"))
        if all(value is not None for value in pose_values):
            pose_str = f"P:{pose_values[0]:.1f}° Y:{pose_values[1]:.1f}° R:{pose_values[2]:.1f}°"
        else:
            pose_str = "P:-- Y:-- R:--"
        self.metrics_table.item(4, 1).setText(pose_str)

        asym = res.get("facial_asymmetry_pct", 0.0)
        if asym is None:
            self.metrics_table.item(5, 1).setText("--")
        else:
            sym_score = max(0.0, 100.0 - asym)
            self.metrics_table.item(5, 1).setText(f"{sym_score:.1f}% (Asym: {asym:.1f}%)")

    def mousePressEvent(self, event):
        """Allows user to react to reaction time test by clicking anywhere in the view."""
        if reaction_test.stimulus_active:
            latency = reaction_test.record_response()
            if latency:
                bus.companion_message_requested.emit(f"Reaction recorded: {latency:.0f} milliseconds. Good reflex latency!", "happy")

    def _toggle_tracking_test(self):
        if not tracking_test.is_active:
            tracking_test.start()
            self.btn_tracking.setText("STOP GUIDED EYE-TRACKING")
            bus.companion_message_requested.emit("Follow the glowing cyan target with your gaze. Measuring smooth pursuit eye coordination.", "thinking")
        else:
            tracking_test.stop()
            self.btn_tracking.setText("1. START GUIDED EYE-TRACKING (SMOOTH PURSUIT)")

    def _toggle_reaction_test(self):
        if not reaction_test.is_waiting_stimulus and not reaction_test.stimulus_active:
            reaction_test.start_trial()
            self.btn_reaction.setText("TEST ACTIVE: CLICK WHEN GREEN APPEARS")
            bus.companion_message_requested.emit("Prepare for visual stimulus. Click or tap immediately when the green box flashes.", "listening")
        else:
            reaction_test.is_waiting_stimulus = False
            reaction_test.stimulus_active = False
            self.btn_reaction.setText("2. START VISUAL REACTION-TIME TEST")

    def _toggle_coordination_test(self):
        if not coordination_test.is_active:
            coordination_test.start()
            self.btn_coordination.setText("COORDINATION DRILL IN PROGRESS...")
            bus.companion_message_requested.emit("Head coordination test active. Follow the on-screen rotation prompts precisely.", "thinking")
        else:
            coordination_test.is_active = False
            self.btn_coordination.setText("3. START GUIDED HEAD-COORDINATION TEST")

    def _on_test_completed(self, result: dict):
        t_type = result.get("test_type")
        if t_type == "GUIDED_EYE_TRACKING":
            self.btn_tracking.setText("1. START GUIDED EYE-TRACKING (SMOOTH PURSUIT)")
            if result["status"] == "INCOMPLETE":
                msg = "Visual tracking incomplete: no valid face samples were captured. Reposition your face and repeat."
            else:
                msg = f"Visual Tracking complete! Mean error: {result['tracking_error_px']}px | Smoothness: {result['smoothness_score_pct']}%"
            bus.companion_message_requested.emit(msg, "happy" if result["status"] == "PASS" else "concerned")
            QMessageBox.information(self, "Eye Tracking Test Results", msg)
        elif t_type == "VISUAL_REACTION_TIME":
            self.btn_reaction.setText("2. START VISUAL REACTION-TIME TEST")
            msg = f"Reaction Test complete! Mean latency: {result['reaction_time_ms']} ms ({result['status']})"
            bus.companion_message_requested.emit(msg, "happy")
            QMessageBox.information(self, "Reaction Test Results", msg)
        elif t_type == "GUIDED_COORDINATION":
            self.btn_coordination.setText("3. START GUIDED HEAD-COORDINATION TEST")
            msg = f"Head Coordination complete! Adherence Score: {result['coordination_score_pct']}% ({result['status']})"
            bus.companion_message_requested.emit(msg, "happy")
            QMessageBox.information(self, "Coordination Test Results", msg)

        # Propagate result to event bus & database
        bus.camera_assessment_completed.emit(result)

    def _record_session(self):
        """Persists current visual screening telemetry to SQLite."""
        if self.camera_thread.use_synthetic_feed:
            QMessageBox.warning(
                self,
                "Demo Feed Active",
                "A synthetic demo feed cannot be recorded as a real camera screening. Switch to the physical webcam first.",
            )
            return
        if not self.current_cv_results.get("face_detected"):
            QMessageBox.warning(self, "No Face Lock", "Center your face in the guide and wait for a face lock before recording.")
            return
        if self.viewport.scan_status != "FACE LOCKED - HOLD STILL":
            QMessageBox.warning(self, "Scan Not Ready", f"Follow the camera guidance before recording: {self.viewport.scan_status}.")
            return
        if self.current_cv_results.get("ear") is None:
            QMessageBox.warning(self, "Eyes Not Detected", "Keep both eyes visible to the camera and wait for eye detection before recording.")
            return

        try:
            from datetime import datetime
            now_str = datetime.now().isoformat()
            db_manager.execute_write(
                "INSERT INTO camera_assessments (astronaut_id, timestamp, assessment_type, blink_count, blink_rate_per_min, ear_avg, head_pitch, head_yaw, head_roll, facial_asymmetry_pct, quality_score, status) "
                "VALUES (?, ?, 'ROUTINE_SCREENING', ?, ?, ?, ?, ?, ?, ?, ?, 'COMPLETED')",
                (
                    self.active_astronaut_id,
                    now_str,
                    self.current_cv_results.get("blink_count", 0),
                    self.current_cv_results.get("blink_rate_per_min", 0.0),
                    self.current_cv_results.get("ear", 0.30),
                    self.current_cv_results.get("head_pitch", 0.0),
                    self.current_cv_results.get("head_yaw", 0.0),
                    self.current_cv_results.get("head_roll", 0.0),
                    self.current_cv_results.get("facial_asymmetry_pct", 0.0),
                    self.current_quality.get("quality_score", 95.0)
                )
            )
            log_audit("CAMERA_SCREENING_LOGGED", f"Astronaut: {self.active_astronaut_id}", f"Blinks: {self.current_cv_results.get('blink_count', 0)}")
            QMessageBox.information(self, "Session Recorded", "Visual screening session saved to astronaut medical history.")
        except Exception as e:
            QMessageBox.warning(self, "Recording Error", f"Failed to record session: {e}")

    def shutdown(self):
        """Cleanly stops camera thread upon application shutdown."""
        self.camera_thread.stop()
