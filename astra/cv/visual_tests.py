"""
ASTRA Guided Visual Screening Assessments
Implements:
1. Guided Visual Tracking Test (Sinusoidal target smooth pursuit & Euclidean error calculation)
2. Visual Reaction-Time Test (Randomized stimulus & millisecond reaction latency)
3. Guided Coordination / Head Orientation Assessment (Multi-axis rotational task completion)
"""
import time
import math
import random
from typing import Dict, Any, Optional, List, Tuple
from PySide6.QtCore import QObject, Signal


class VisualTrackingTest(QObject):
    """Calibrated moving target eye-following and smooth pursuit tracking test."""

    test_completed = Signal(dict)

    def __init__(self, duration_seconds: float = 10.0, parent=None):
        super().__init__(parent)
        self.duration = duration_seconds
        self.start_time: Optional[float] = None
        self.is_active = False
        self.tracking_errors: List[float] = []

    def start(self):
        self.is_active = True
        self.start_time = time.time()
        self.tracking_errors.clear()

    def stop(self) -> Dict[str, Any]:
        self.is_active = False
        avg_err = float(np.mean(self.tracking_errors)) if self.tracking_errors else 0.0
        # Smoothness score (0-100%): 0 error -> 100%, >50px error -> <50%
        smoothness = max(0.0, min(100.0, 100.0 - avg_err * 1.5))
        result = {
            "test_type": "GUIDED_EYE_TRACKING",
            "duration_sec": self.duration,
            "sample_count": len(self.tracking_errors),
            "tracking_error_px": round(avg_err, 1) if self.tracking_errors else None,
            "smoothness_score_pct": round(smoothness, 1) if self.tracking_errors else None,
            "status": "INCOMPLETE" if not self.tracking_errors else ("PASS" if avg_err < 30.0 else "DEGRADED")
        }
        self.test_completed.emit(result)
        return result

    def get_target_position(self, frame_w: int, frame_h: int) -> Tuple[int, int]:
        """Calculates current calibrated target coordinate on a smooth Lissajous path."""
        if not self.is_active or not self.start_time:
            return (frame_w // 2, frame_h // 2)

        elapsed = time.time() - self.start_time
        if elapsed >= self.duration:
            self.stop()
            return (frame_w // 2, frame_h // 2)

        # Lissajous curve parameters
        cx = frame_w / 2.0
        cy = frame_h / 2.0
        rx = frame_w * 0.35
        ry = frame_h * 0.28
        tx = int(cx + rx * math.sin(elapsed * 1.6))
        ty = int(cy + ry * math.sin(elapsed * 2.4))
        return (tx, ty)

    def record_sample(self, target_pos: Tuple[int, int], detected_face_center: Tuple[int, int]):
        """Records distance error between target and astronaut visual center."""
        if not self.is_active:
            return
        dx = target_pos[0] - detected_face_center[0]
        dy = target_pos[1] - detected_face_center[1]
        dist = math.hypot(dx, dy)
        self.tracking_errors.append(dist)


class VisualReactionTest(QObject):
    """Measures cognitive-visual stimulus response latency in milliseconds."""

    test_completed = Signal(dict)
    stimulus_shown = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_waiting_stimulus = False
        self.stimulus_active = False
        self.trigger_time: Optional[float] = None
        self.start_wait_time: Optional[float] = None
        self.delay_duration: float = 2.5
        self.trials: List[float] = []
        self.max_trials = 3

    def start_trial(self):
        """Begins randomized delay before visual stimulus appears."""
        self.is_waiting_stimulus = True
        self.stimulus_active = False
        self.start_wait_time = time.time()
        self.delay_duration = random.uniform(1.8, 3.8)

    def update(self) -> bool:
        """Call periodically; returns True if stimulus is now active."""
        if self.is_waiting_stimulus and self.start_wait_time:
            if time.time() - self.start_wait_time >= self.delay_duration:
                self.is_waiting_stimulus = False
                self.stimulus_active = True
                self.trigger_time = time.time()
                self.stimulus_shown.emit()
        return self.stimulus_active

    def record_response(self) -> Optional[float]:
        """User reacted; records elapsed time."""
        if not self.stimulus_active or not self.trigger_time:
            return None

        latency_ms = (time.time() - self.trigger_time) * 1000.0
        self.stimulus_active = False
        self.trials.append(latency_ms)

        if len(self.trials) >= self.max_trials:
            avg_ms = float(np.mean(self.trials))
            result = {
                "test_type": "VISUAL_REACTION_TIME",
                "trials_count": len(self.trials),
                "reaction_time_ms": round(avg_ms, 1),
                "all_trials_ms": [round(t, 1) for t in self.trials],
                "status": "PASS" if avg_ms < 380.0 else "SLUGGISH"
            }
            self.test_completed.emit(result)
            self.trials.clear()
            return avg_ms

        # Start next trial
        self.start_trial()
        return latency_ms


class GuidedCoordinationTest(QObject):
    """Guides astronaut through defined head rotational orientations to evaluate vestibular motor stability."""

    test_completed = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.stages = [
            {"name": "Center Baseline", "target_pitch": 0.0, "target_yaw": 0.0, "tol": 8.0, "duration": 3.0},
            {"name": "Look Up (Pitch +15°)", "target_pitch": 15.0, "target_yaw": 0.0, "tol": 10.0, "duration": 3.0},
            {"name": "Look Left (Yaw -20°)", "target_pitch": 0.0, "target_yaw": -20.0, "tol": 10.0, "duration": 3.0},
            {"name": "Look Right (Yaw +20°)", "target_pitch": 0.0, "target_yaw": 20.0, "tol": 10.0, "duration": 3.0},
            {"name": "Return Center", "target_pitch": 0.0, "target_yaw": 0.0, "tol": 8.0, "duration": 3.0}
        ]
        self.current_stage_idx = 0
        self.is_active = False
        self.stage_start_time = 0.0
        self.stage_adherence_scores: List[float] = []

    def start(self):
        self.is_active = True
        self.current_stage_idx = 0
        self.stage_start_time = time.time()
        self.stage_adherence_scores.clear()

    def update(self, current_pitch: float, current_yaw: float) -> Dict[str, Any]:
        if not self.is_active or self.current_stage_idx >= len(self.stages):
            return {"active": False}

        stage = self.stages[self.current_stage_idx]
        elapsed = time.time() - self.stage_start_time

        dp = abs(current_pitch - stage["target_pitch"])
        dy = abs(current_yaw - stage["target_yaw"])
        on_target = (dp <= stage["tol"] and dy <= stage["tol"])

        if elapsed >= stage["duration"]:
            # Record stage score
            score = max(0.0, 100.0 - (dp + dy) * 3.0)
            self.stage_adherence_scores.append(score)
            self.current_stage_idx += 1
            self.stage_start_time = time.time()

            if self.current_stage_idx >= len(self.stages):
                self.is_active = False
                mean_score = float(np.mean(self.stage_adherence_scores)) if self.stage_adherence_scores else 0.0
                res = {
                    "test_type": "GUIDED_COORDINATION",
                    "coordination_score_pct": round(mean_score, 1),
                    "stages_completed": len(self.stages),
                    "status": "PASS" if mean_score >= 60.0 else "IMPAIRED"
                }
                self.test_completed.emit(res)
                return res

        return {
            "active": True,
            "stage_name": stage["name"],
            "target_pitch": stage["target_pitch"],
            "target_yaw": stage["target_yaw"],
            "current_pitch": current_pitch,
            "current_yaw": current_yaw,
            "on_target": on_target,
            "stage_index": self.current_stage_idx + 1,
            "total_stages": len(self.stages)
        }


import numpy as np
tracking_test = VisualTrackingTest()
reaction_test = VisualReactionTest()
coordination_test = GuidedCoordinationTest()
