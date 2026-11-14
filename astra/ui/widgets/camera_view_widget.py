"""
ASTRA Camera Viewport Widget
Displays live webcam video feed with PySide6 QPixmap conversion,
interactive test targets, calibration reticles, and reaction stimulus overlays.
"""
from typing import Optional, Tuple
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QImage, QPixmap, QPainter, QColor, QPen, QBrush, QFont
import numpy as np


class CameraViewportWidget(QWidget):
    """High-performance video viewport rendering OpenCV frames and interactive test overlays."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(360, 270)
        self.current_pixmap: Optional[QPixmap] = None
        self.frame_size = (640, 480)
        self.scan_status = "CENTER YOUR FACE IN THE GUIDE"
        self.face_aligned = False

        # Interactive test states
        self.tracking_target_pos: Optional[Tuple[int, int]] = None
        self.show_reaction_stimulus = False
        self.coordination_prompt = ""

    def update_frame(self, bgr_frame: np.ndarray):
        """Converts raw OpenCV BGR frame into QPixmap for high-speed rendering."""
        if bgr_frame is None or bgr_frame.size == 0:
            return

        h, w, ch = bgr_frame.shape
        self.frame_size = (w, h)
        bytes_per_line = ch * w
        
        # Fast conversion from BGR to RGB QImage
        rgb_data = np.ascontiguousarray(bgr_frame[:, :, ::-1])
        q_img = QImage(rgb_data.data, w, h, bytes_per_line, QImage.Format_RGB888).copy()
        self.current_pixmap = QPixmap.fromImage(q_img)
        self.update()

    def set_scan_status(self, text: str, face_aligned: bool):
        self.scan_status = text
        self.face_aligned = face_aligned
        self.update()

    def set_tracking_target(self, pos: Optional[Tuple[int, int]]):
        self.tracking_target_pos = pos
        self.update()

    def set_reaction_stimulus(self, active: bool):
        self.show_reaction_stimulus = active
        self.update()

    def set_coordination_prompt(self, text: str):
        self.coordination_prompt = text
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()

        # Background Fill
        painter.fillRect(0, 0, w, h, QColor(10, 14, 23))

        image_rect = QRectF(0, 0, w, h)

        # 1. Render Video Frame
        if self.current_pixmap and not self.current_pixmap.isNull():
            scaled = self.current_pixmap.scaled(w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px = (w - scaled.width()) // 2
            py = (h - scaled.height()) // 2
            painter.drawPixmap(px, py, scaled)
            image_rect = QRectF(px, py, scaled.width(), scaled.height())
        else:
            painter.setPen(QPen(QColor(148, 163, 184), 1))
            painter.setFont(QFont("Segoe UI", 12))
            painter.drawText(QRectF(0, 0, w, h), Qt.AlignCenter, "INITIALIZING CAMERA SENSOR FEED...")

        # 2. Face-position grid and live scan guidance
        painter.setPen(QPen(QColor(0, 229, 255, 75), 1, Qt.DashLine))
        for column in (1, 2):
            x = image_rect.left() + image_rect.width() * column / 3
            painter.drawLine(QPointF(x, image_rect.top()), QPointF(x, image_rect.bottom()))
        for row in (1, 2):
            y = image_rect.top() + image_rect.height() * row / 3
            painter.drawLine(QPointF(image_rect.left(), y), QPointF(image_rect.right(), y))

        guide_rect = QRectF(
            image_rect.left() + image_rect.width() * 0.27,
            image_rect.top() + image_rect.height() * 0.10,
            image_rect.width() * 0.46,
            image_rect.height() * 0.78,
        )
        guide_color = QColor(0, 230, 118, 210) if self.face_aligned else QColor(0, 229, 255, 190)
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(guide_color, 2, Qt.DashLine))
        painter.drawEllipse(guide_rect)

        status_rect = QRectF(
            image_rect.left() + 8,
            image_rect.bottom() - 34,
            max(0, image_rect.width() - 16),
            26,
        )
        painter.setBrush(QColor(10, 14, 23, 205))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(status_rect, 5, 5)
        painter.setPen(QColor(0, 230, 118) if self.face_aligned else QColor(255, 179, 0))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(status_rect, Qt.AlignCenter, self.scan_status)

        # 2. Render Guided Visual Tracking Target
        if self.tracking_target_pos:
            tx, ty = self.tracking_target_pos
            frame_w, frame_h = self.frame_size
            scale_x = image_rect.width() / frame_w
            scale_y = image_rect.height() / frame_h
            scr_x = image_rect.left() + tx * scale_x
            scr_y = image_rect.top() + ty * scale_y

            # Glowing Target Outer Rings
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(0, 229, 255, 180), 2.5))
            painter.drawEllipse(QPointF(scr_x, scr_y), 18, 18)
            painter.setPen(QPen(QColor(0, 229, 255, 100), 1.5, Qt.DashLine))
            painter.drawEllipse(QPointF(scr_x, scr_y), 28, 28)

            # Target Center Dot
            painter.setBrush(QBrush(QColor(0, 230, 118)))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(QPointF(scr_x, scr_y), 5, 5)

        # 4. Render Visual Reaction Stimulus
        if self.show_reaction_stimulus:
            painter.setBrush(QBrush(QColor(0, 230, 118, 200))) # Bright green flash
            painter.setPen(QPen(QColor(255, 255, 255), 3))
            stim_rect = QRectF(w / 2 - 120, h / 2 - 50, 240, 100)
            painter.drawRoundedRect(stim_rect, 10, 10)

            painter.setPen(QColor(10, 14, 23))
            painter.setFont(QFont("Segoe UI", 16, QFont.Bold))
            painter.drawText(stim_rect, Qt.AlignCenter, "REACT NOW!\n[CLICK / TAP]")

        # 5. Render Guided Coordination Target Prompt
        if self.coordination_prompt:
            p_rect = QRectF(20, 20, w - 40, 36)
            painter.setBrush(QBrush(QColor(18, 26, 42, 220)))
            painter.setPen(QPen(QColor(0, 229, 255), 1.5))
            painter.drawRoundedRect(p_rect, 6, 6)

            painter.setPen(QColor(240, 244, 252))
            painter.setFont(QFont("Segoe UI", 11, QFont.Bold))
            painter.drawText(p_rect, Qt.AlignCenter, self.coordination_prompt)
