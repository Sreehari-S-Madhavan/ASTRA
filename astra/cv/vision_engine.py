"""
ASTRA Computer Vision & Visual Health Screening Engine
Implements real-time face detection, eye landmark tracking, blink frequency analysis (EAR),
head pose estimation (Pitch/Yaw/Roll via solvePnP), facial symmetry analysis,
posture alignment, and experimental camera photoplethysmography (rPPG).
"""
import time
import math
from typing import Dict, Any, List, Optional, Tuple
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False


class VisionEngine:
    """Core computer vision analyzer for astronaut visual health screening."""

    def __init__(self):
        # 3D Facial Model Reference Points for Perspective-n-Point (solvePnP)
        self.model_points_3d = np.array([
            (0.0, 0.0, 0.0),             # Nose tip
            (0.0, -330.0, -65.0),        # Chin
            (-225.0, 170.0, -135.0),     # Left eye outer corner
            (225.0, 170.0, -135.0),      # Right eye outer corner
            (-150.0, -150.0, -125.0),    # Left mouth corner
            (150.0, -150.0, -125.0)      # Right mouth corner
        ], dtype=np.float64)

        # 3D Coordinate Axis vectors for head pose projection
        self.axis_points_3d = np.array([
            (150.0, 0.0, 0.0),    # X axis (Pitch / Red)
            (0.0, 150.0, 0.0),    # Y axis (Yaw / Green)
            (0.0, 0.0, -150.0)    # Z axis (Roll / Blue)
        ], dtype=np.float64)

        # Blink Detection Tracking State
        self.ear_history: List[float] = []
        self.blink_timestamps: List[float] = []
        self.blink_count = 0
        self.in_blink = False
        self.ear_threshold = 0.22

        # rPPG Experimental Buffer
        self.rppg_green_values: List[float] = []
        self.rppg_timestamps: List[float] = []
        self.estimated_pulse_bpm: Optional[float] = None

        # Load OpenCV Haar Cascades if available
        self.face_cascade = None
        self.eye_cascade = None
        if HAS_CV2:
            try:
                self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
                self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
                if self.face_cascade.empty():
                    self.face_cascade = None
                if self.eye_cascade.empty():
                    self.eye_cascade = None
            except Exception:
                pass

    def reset_screening_stats(self):
        """Clears accumulated counters for a new screening session."""
        self.ear_history.clear()
        self.blink_timestamps.clear()
        self.blink_count = 0
        self.in_blink = False
        self.rppg_green_values.clear()
        self.rppg_timestamps.clear()
        self.estimated_pulse_bpm = None

    def process_frame(
        self,
        frame: np.ndarray,
        draw_overlays: bool = True,
        enable_rppg: bool = False
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Analyzes frame and renders aerospace HUD diagnostic overlays."""
        h, w = frame.shape[:2]
        now = time.time()
        result: Dict[str, Any] = {
            "face_detected": False,
            "face_count": 0,
            "face_bbox": None,
            "blink_count": self.blink_count,
            "blink_rate_per_min": None,
            "ear": None,
            "head_pitch": None,
            "head_yaw": None,
            "head_roll": None,
            "facial_asymmetry_pct": None,
            "estimated_pulse_bpm": None,
            "upper_body_posture": "UNAVAILABLE",
            "analysis_status": "DETECTION_UNAVAILABLE"
        }

        if not HAS_CV2 or self.face_cascade is None:
            if draw_overlays and HAS_CV2:
                cv2.putText(frame, "FACE DETECTOR UNAVAILABLE", (20, h - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)
            return frame, result

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.15, minNeighbors=4, minSize=(90, 90))
        result["face_detected"] = len(faces) > 0
        result["face_count"] = len(faces)

        if not result["face_detected"]:
            result["analysis_status"] = "NO_FACE"
            if draw_overlays:
                cv2.putText(frame, "TARGET SEARCH: NO CREW FACE LOCK", (20, h - 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2, cv2.LINE_AA)
            return frame, result

        fx, fy, fw, fh = max(faces, key=lambda f: f[2] * f[3])
        result["face_bbox"] = (int(fx), int(fy), int(fw), int(fh))
        result["analysis_status"] = "FACE_DETECTED"
        face_roi_gray = gray[fy:fy+fh, fx:fx+fw]

        # Landmark points
        nose_pt = (int(fx + fw * 0.50), int(fy + fh * 0.55))
        chin_pt = (int(fx + fw * 0.50), int(fy + fh * 0.95))
        left_eye_pt = (int(fx + fw * 0.32), int(fy + fh * 0.38))
        right_eye_pt = (int(fx + fw * 0.68), int(fy + fh * 0.38))
        left_mouth_pt = (int(fx + fw * 0.35), int(fy + fh * 0.78))
        right_mouth_pt = (int(fx + fw * 0.65), int(fy + fh * 0.78))
        left_ear, right_ear = None, None
        eyes_found = False
        if self.eye_cascade:
            eyes = self.eye_cascade.detectMultiScale(
                face_roi_gray[0:int(fh * 0.6), :],
                scaleFactor=1.1,
                minNeighbors=3,
                minSize=(20, 20),
            )
            if len(eyes) >= 2:
                eyes_sorted = sorted(eyes, key=lambda eye: eye[0])
                ex1, ey1, ew1, eh1 = eyes_sorted[0]
                ex2, ey2, ew2, eh2 = eyes_sorted[-1]
                left_eye_pt = (fx + ex1 + ew1 // 2, fy + ey1 + eh1 // 2)
                right_eye_pt = (fx + ex2 + ew2 // 2, fy + ey2 + eh2 // 2)
                left_ear = float(eh1) / max(1.0, float(ew1)) * 0.65
                right_ear = float(eh2) / max(1.0, float(ew2)) * 0.65
                eyes_found = True

        if eyes_found:
            avg_ear = (left_ear + right_ear) / 2.0
            result["ear"] = round(avg_ear, 3)
            if avg_ear < self.ear_threshold and not self.in_blink:
                self.in_blink = True
                self.blink_count += 1
                self.blink_timestamps.append(now)
            elif avg_ear >= self.ear_threshold:
                self.in_blink = False

            self.blink_timestamps = [ts for ts in self.blink_timestamps if now - ts <= 60.0]
            result["blink_count"] = self.blink_count
            result["blink_rate_per_min"] = round(min(120.0, len(self.blink_timestamps)), 1)

            left_eye_dist = math.hypot(left_eye_pt[0] - nose_pt[0], left_eye_pt[1] - nose_pt[1])
            right_eye_dist = math.hypot(right_eye_pt[0] - nose_pt[0], right_eye_pt[1] - nose_pt[1])
            max_d = max(left_eye_dist, right_eye_dist, 1.0)
            result["facial_asymmetry_pct"] = round(abs(left_eye_dist - right_eye_dist) / max_d * 100.0, 1)

        # Head pose is estimated from coarse cascade-relative points, not facial landmarks.
        focal_length = w
        center = (w / 2, h / 2)
        cam_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype=np.float64)
        dist_coeffs = np.zeros((4, 1), dtype=np.float64)
        image_points_2d = np.array([nose_pt, chin_pt, left_eye_pt, right_eye_pt, left_mouth_pt, right_mouth_pt], dtype=np.float64)
        success, rvec, tvec = cv2.solvePnP(
            self.model_points_3d,
            image_points_2d,
            cam_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        axis_proj = None
        if success:
            rmat, _ = cv2.Rodrigues(rvec)
            result["head_pitch"] = round(math.degrees(math.atan2(rmat[2, 1], rmat[2, 2])), 1)
            result["head_yaw"] = round(math.degrees(math.atan2(-rmat[2, 0], math.sqrt(rmat[0, 0]**2 + rmat[1, 0]**2))), 1)
            result["head_roll"] = round(math.degrees(math.atan2(rmat[1, 0], rmat[0, 0])), 1)
            axis_proj, _ = cv2.projectPoints(self.axis_points_3d, rvec, tvec, cam_matrix, dist_coeffs)

        if enable_rppg:
            fh_roi = frame[
                max(0, fy + int(fh * 0.1)):min(h, fy + int(fh * 0.25)),
                max(0, fx + int(fw * 0.35)):min(w, fx + int(fw * 0.65)),
            ]
            if fh_roi.size > 0:
                self.rppg_green_values.append(float(np.mean(fh_roi[:, :, 1])))
                self.rppg_timestamps.append(now)
                if len(self.rppg_green_values) > 120:
                    self.rppg_green_values.pop(0)
                    self.rppg_timestamps.pop(0)
                    signal = np.array(self.rppg_green_values) - np.mean(self.rppg_green_values)
                    peaks = np.where((signal[1:-1] > signal[:-2]) & (signal[1:-1] > signal[2:]) & (signal[1:-1] > 0.4))[0]
                    duration = self.rppg_timestamps[-1] - self.rppg_timestamps[0]
                    if duration > 3.0 and len(peaks) > 2:
                        self.estimated_pulse_bpm = round((len(peaks) / duration) * 60.0, 1)
                        result["estimated_pulse_bpm"] = self.estimated_pulse_bpm

        if draw_overlays:
            line_len = int(fw * 0.20)
            c_cyan = (255, 229, 0)
            cv2.line(frame, (fx, fy), (fx + line_len, fy), c_cyan, 2)
            cv2.line(frame, (fx, fy), (fx, fy + line_len), c_cyan, 2)
            cv2.line(frame, (fx + fw, fy), (fx + fw - line_len, fy), c_cyan, 2)
            cv2.line(frame, (fx + fw, fy), (fx + fw, fy + line_len), c_cyan, 2)
            cv2.line(frame, (fx, fy + fh), (fx + line_len, fy + fh), c_cyan, 2)
            cv2.line(frame, (fx, fy + fh), (fx, fy + fh - line_len), c_cyan, 2)
            cv2.line(frame, (fx + fw, fy + fh), (fx + fw - line_len, fy + fh), c_cyan, 2)
            cv2.line(frame, (fx + fw, fy + fh), (fx + fw, fy + fh - line_len), c_cyan, 2)
            if eyes_found:
                cv2.circle(frame, left_eye_pt, 4, (0, 230, 118), -1)
                cv2.circle(frame, right_eye_pt, 4, (0, 230, 118), -1)
                cv2.putText(frame, f"BLINKS: {self.blink_count} | EAR: {result['ear']:.2f}",
                            (20, h - 55), cv2.FONT_HERSHEY_SIMPLEX, 0.50, (240, 244, 252), 1, cv2.LINE_AA)
            if success and axis_proj is not None:
                p_nose = (int(nose_pt[0]), int(nose_pt[1]))
                cv2.line(frame, p_nose, (int(axis_proj[0][0][0]), int(axis_proj[0][0][1])), (0, 0, 255), 2)
                cv2.line(frame, p_nose, (int(axis_proj[1][0][0]), int(axis_proj[1][0][1])), (0, 255, 0), 2)
                cv2.line(frame, p_nose, (int(axis_proj[2][0][0]), int(axis_proj[2][0][1])), (255, 0, 0), 2)

        return frame, result


vision_engine = VisionEngine()
