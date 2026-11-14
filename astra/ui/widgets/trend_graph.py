"""
ASTRA Real-Time Trend Graph Widget
Vector-rendered real-time telemetry curve rendered using PySide6 QPainter.
Displays moving time-series curves, safe physiological thresholds, and grid lines.
"""
from typing import List, Optional
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF, QRectF
from PySide6.QtGui import QPainter, QColor, QPen, QBrush, QFont, QLinearGradient
from astra.config import THEME


class TrendGraph(QWidget):
    """Real-time scrolling trend chart with physiological safe-zone shading."""

    def __init__(
        self,
        title: str,
        unit: str = "",
        min_y: float = 40.0,
        max_y: float = 160.0,
        safe_min: Optional[float] = 60.0,
        safe_max: Optional[float] = 100.0,
        max_points: int = 50,
        color_hex: str = "#00E5FF",
        parent=None
    ):
        super().__init__(parent)
        self.title = title
        self.unit = unit
        self.min_y = min_y
        self.max_y = max_y
        self.safe_min = safe_min
        self.safe_max = safe_max
        self.max_points = max_points
        self.line_color = QColor(color_hex)
        self.data_points: List[float] = []

        self.setMinimumHeight(130)

    def add_point(self, val: Optional[float]):
        if val is not None:
            self.data_points.append(val)
            if len(self.data_points) > self.max_points:
                self.data_points.pop(0)
            self.update()

    def set_data(self, values: List[float]):
        self.data_points = values[-self.max_points:]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        pad_l, pad_r, pad_t, pad_b = 38.0, 15.0, 24.0, 20.0
        plot_w = w - pad_l - pad_r
        plot_h = h - pad_t - pad_b

        # 1. Background Fill
        painter.fillRect(QRectF(0, 0, w, h), QColor(THEME['bg_surface']))
        painter.setPen(QPen(QColor(THEME['border']), 1))
        painter.drawRect(QRectF(0, 0, w - 1, h - 1))

        # 2. Safe Threshold Zone Shading
        if self.safe_min is not None and self.safe_max is not None and plot_h > 0:
            y_span = max(1.0, self.max_y - self.min_y)
            top_y = pad_t + plot_h * (1.0 - (self.safe_max - self.min_y) / y_span)
            bot_y = pad_t + plot_h * (1.0 - (self.safe_min - self.min_y) / y_span)
            safe_rect = QRectF(pad_l, top_y, plot_w, max(2.0, bot_y - top_y))
            painter.fillRect(safe_rect, QColor(0, 230, 118, 20)) # Light green tint

        # 3. Grid Lines & Y-Axis Labels
        painter.setFont(QFont("Segoe UI", 8))
        grid_steps = 4
        for i in range(grid_steps + 1):
            fraction = float(i) / grid_steps
            gy = pad_t + plot_h * (1.0 - fraction)
            gval = self.min_y + (self.max_y - self.min_y) * fraction

            painter.setPen(QPen(QColor(THEME['border']), 1, Qt.DotLine))
            painter.drawLine(QPointF(pad_l, gy), QPointF(pad_l + plot_w, gy))

            painter.setPen(QPen(QColor(THEME['text_muted'])))
            painter.drawText(QRectF(2, gy - 8, pad_l - 6, 16), Qt.AlignRight | Qt.AlignVCenter, f"{gval:.0f}")

        # 4. Header Label
        curr_val_txt = f"{self.data_points[-1]:.1f} {self.unit}" if self.data_points else "--"
        painter.setPen(QPen(QColor(THEME['text_primary'])))
        painter.setFont(QFont("Segoe UI", 9, QFont.Bold))
        painter.drawText(QRectF(pad_l, 4, plot_w, 18), Qt.AlignLeft | Qt.AlignVCenter, f"{self.title.upper()} ({curr_val_txt})")

        # 5. Telemetry Data Curve & Area Fill
        n = len(self.data_points)
        if n >= 2 and plot_w > 0 and plot_h > 0:
            y_span = max(1.0, self.max_y - self.min_y)
            points = []
            for i, val in enumerate(self.data_points):
                clamped_val = max(self.min_y, min(self.max_y, val))
                x = pad_l + (float(i) / (self.max_points - 1)) * plot_w
                y = pad_t + plot_h * (1.0 - (clamped_val - self.min_y) / y_span)
                points.append(QPointF(x, y))

            # Draw glowing line
            curve_pen = QPen(self.line_color, 2.0)
            painter.setPen(curve_pen)
            for i in range(len(points) - 1):
                painter.drawLine(points[i], points[i + 1])

            # Draw current head dot
            last_pt = points[-1]
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.setPen(QPen(self.line_color, 2.0))
            painter.drawEllipse(last_pt, 3.5, 3.5)
