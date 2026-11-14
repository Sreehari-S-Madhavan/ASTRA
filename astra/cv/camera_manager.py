"""
ASTRA Camera Manager
Manages webcam acquisition via OpenCV (with pure NumPy fallback if OpenCV is installing/absent)
in a high-performance PySide6 QThread, with device enumeration, camera quality assessment,
disconnect testing, and automatic procedural astronaut synthetic test feed fallback.
"""
import time
import math
import random
from typing import Optional, Tuple
from PySide6.QtCore import QThread, Signal, QMutex
import numpy as np

try:
    import cv2
    HAS_CV2 = True
except ImportError:
    cv2 = None
    HAS_CV2 = False


class CameraQualityMetrics:
    """Calculates illumination, contrast, sharpness, and visibility of the frame."""

    @staticmethod
    def evaluate(frame: np.ndarray) -> dict:
        if frame is None or frame.size == 0:
            return {"brightness": 0.0, "contrast": 0.0, "sharpness": 0.0, "quality_score": 0.0, "status": "NO_FRAME"}

        if HAS_CV2:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            sharpness = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        else:
            # Grayscale via standard luminance weights (0.299 R, 0.587 G, 0.114 B)
            gray = frame[:, :, 0] * 0.114 + frame[:, :, 1] * 0.587 + frame[:, :, 2] * 0.299
            # Approximation of sharpness via finite differences
            diff_y = np.diff(gray, axis=0)
            diff_x = np.diff(gray, axis=1)
            sharpness = float(np.var(diff_y) + np.var(diff_x)) * 0.5

        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        # Quality scoring (0-100)
        b_score = max(0.0, 100.0 - abs(brightness - 130.0) * 1.1)
        c_score = min(100.0, (contrast / 45.0) * 100.0)
        s_score = min(100.0, (sharpness / 80.0) * 100.0)
        quality_score = round(b_score * 0.35 + c_score * 0.35 + s_score * 0.30, 1)

        status = "EXCELLENT" if quality_score >= 80 else ("ACCEPTABLE" if quality_score >= 50 else "LOW_QUALITY")
        if brightness < 40:
            status = "LOW_LIGHT"
        elif brightness > 220:
            status = "OVEREXPOSED"
        elif sharpness < 15:
            status = "BLURRY"

        return {
            "brightness": round(brightness, 1),
            "contrast": round(contrast, 1),
            "sharpness": round(sharpness, 1),
            "quality_score": quality_score,
            "status": status
        }


class CameraThread(QThread):
    """Worker thread streaming video frames without blocking GUI."""

    frame_ready = Signal(np.ndarray, dict)  # (frame, quality_metrics)
    camera_status_changed = Signal(str, str) # (status, message)

    def __init__(self, device_index: int = 0, parent=None):
        super().__init__(parent)
        self.device_index = device_index
        self._running = False
        self._paused = False
        self._mutex = QMutex()
        self.use_synthetic_feed = not HAS_CV2
        self.cap = None
        self._synthetic_frame_count = 0

    def run(self):
        self._running = True
        if HAS_CV2 and not self.use_synthetic_feed:
            self._open_camera()
        else:
            self.use_synthetic_feed = True
            self.camera_status_changed.emit("SYNTHETIC_MODE", "Active procedural astronaut test feed.")

        while self._running:
            if self._paused:
                self.msleep(100)
                continue

            frame = None
            if HAS_CV2 and not self.use_synthetic_feed and self.cap and self.cap.isOpened():
                ret, frame = self.cap.read()
                if not ret or frame is None:
                    self.camera_status_changed.emit("FALLBACK", "Physical camera frame drop; activating procedural astronaut test feed.")
                    self.use_synthetic_feed = True

            if self.use_synthetic_feed or frame is None:
                frame = self._generate_synthetic_astronaut_feed()

            metrics = CameraQualityMetrics.evaluate(frame)
            self.frame_ready.emit(frame, metrics)
            self.msleep(33)  # ~30 FPS

        self._close_camera()

    def _open_camera(self):
        if not HAS_CV2:
            self.use_synthetic_feed = True
            return
        try:
            self.cap = cv2.VideoCapture(self.device_index, cv2.CAP_DSHOW)
            if not self.cap or not self.cap.isOpened():
                self.cap = cv2.VideoCapture(self.device_index)

            if self.cap and self.cap.isOpened():
                self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
                self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
                self.use_synthetic_feed = False
                self.camera_status_changed.emit("CONNECTED", f"Webcam #{self.device_index} online (640x480).")
            else:
                self.use_synthetic_feed = True
                self.camera_status_changed.emit("SYNTHETIC_MODE", "Webcam hardware not detected. Active procedural astronaut simulation feed.")
        except Exception as e:
            self.use_synthetic_feed = True
            self.camera_status_changed.emit("SYNTHETIC_MODE", f"Webcam init exception: {e}. Active procedural astronaut simulation feed.")

    def _close_camera(self):
        if self.cap:
            try:
                self.cap.release()
            except Exception:
                pass
            self.cap = None
        self.camera_status_changed.emit("DISCONNECTED", "Camera offline.")

    def stop(self):
        self._running = False
        self.wait(1500)

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def toggle_synthetic(self):
        if not HAS_CV2:
            self.camera_status_changed.emit("SYNTHETIC_MODE", "OpenCV not present; maintaining procedural test feed.")
            return
        self.use_synthetic_feed = not self.use_synthetic_feed
        mode = "Procedural Synthetic Astronaut" if self.use_synthetic_feed else "Physical Webcam"
        self.camera_status_changed.emit("MODE_TOGGLE", f"Switched stream source to: {mode}")

    def _generate_synthetic_astronaut_feed(self) -> np.ndarray:
        """Procedurally renders a synthetic astronaut face feed with natural blinks and head motion."""
        self._synthetic_frame_count += 1
        t = self._synthetic_frame_count * 0.05
        
        # Deep space habitat background (480 x 640 x 3 BGR)
        frame = np.full((480, 640, 3), (25, 20, 15), dtype=np.uint8)

        # Head motion coordinates
        head_x = int(320 + math.sin(t * 0.8) * 18.0)
        head_y = int(240 + math.cos(t * 0.6) * 10.0)

        # Draw procedural face and suit using OpenCV or NumPy rasterization
        if HAS_CV2:
            cv2.circle(frame, (320, 100), 300, (40, 35, 30), -1)
            cv2.ellipse(frame, (head_x, head_y + 240), (190, 120), 0, 0, 360, (50, 40, 30), -1)
            cv2.ellipse(frame, (head_x, head_y + 240), (180, 110), 0, 0, 360, (30, 70, 90), -1)
            cv2.ellipse(frame, (head_x, head_y), (85, 115), 0, 0, 360, (185, 205, 225), -1)

            blink_cycle = (self._synthetic_frame_count % 90)
            is_blink = blink_cycle > 85
            eye_ry = 2 if is_blink else 8
            eye_left_x = head_x - 32
            eye_right_x = head_x + 32
            eye_y = head_y - 12

            cv2.ellipse(frame, (eye_left_x, eye_y), (14, max(2, eye_ry)), 0, 0, 360, (245, 245, 245), -1)
            cv2.ellipse(frame, (eye_right_x, eye_y), (14, max(2, eye_ry)), 0, 0, 360, (245, 245, 245), -1)

            if not is_blink:
                iris_dx = int(math.sin(t * 1.5) * 3)
                cv2.circle(frame, (eye_left_x + iris_dx, eye_y), 5, (90, 60, 40), -1)
                cv2.circle(frame, (eye_right_x + iris_dx, eye_y), 5, (90, 60, 40), -1)

            cv2.putText(frame, "ASTRA SIMULATED TEST FEED [SYNTHETIC ASTRONAUT]", (15, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 229, 255), 1, cv2.LINE_AA)
            cv2.putText(frame, f"FRAME: {self._synthetic_frame_count:05d} | STATUS: CALIBRATED", (15, 52),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (148, 163, 184), 1, cv2.LINE_AA)
        else:
            # Pure NumPy rasterized face block
            # Flight suit shoulders
            y1 = max(0, min(480, head_y + 120))
            frame[y1:480, max(0, head_x - 180):min(640, head_x + 180)] = [30, 70, 90]
            # Face box
            fy1, fy2 = max(0, head_y - 100), min(480, head_y + 100)
            fx1, fx2 = max(0, head_x - 80), min(640, head_x + 80)
            frame[fy1:fy2, fx1:fx2] = [185, 205, 225]
            # Eyes
            ey = head_y - 12
            blink_cycle = (self._synthetic_frame_count % 90)
            is_blink = blink_cycle > 85
            eh = 2 if is_blink else 10
            frame[ey-eh:ey+eh, head_x-42:head_x-18] = [245, 245, 245]
            frame[ey-eh:ey+eh, head_x+18:head_x+42] = [245, 245, 245]

        return frame
