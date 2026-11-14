"""
ASTRA Metric Card Widget
Glassmorphic telemetry card displaying real-time physiological or environmental indicators,
safe threshold bounds, dynamic color-coded status badges, and sparkline progress bars.
"""
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QProgressBar
from PySide6.QtCore import Qt
from astra.config import THEME


class MetricCard(QFrame):
    """Visual telemetry card with status indicator and threshold bar."""

    def __init__(
        self,
        title: str,
        unit: str = "",
        normal_min: Optional[float] = None,
        normal_max: Optional[float] = None,
        parent=None
    ):
        super().__init__(parent)
        self.title_text = title
        self.unit_text = unit
        self.normal_min = normal_min
        self.normal_max = normal_max
        self.current_value: Optional[float] = None
        self.status = "NOMINAL"

        self.setObjectName("metricCard")
        self.setMinimumSize(160, 115)
        self._setup_ui()
        self._update_style()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(4)

        # Header Row (Title + Status Badge)
        hdr = QHBoxLayout()
        self.lbl_title = QLabel(self.title_text.upper())
        self.lbl_title.setStyleSheet(f"color: {THEME['text_secondary']}; font-size: 10px; font-weight: bold; letter-spacing: 0.5px;")
        hdr.addWidget(self.lbl_title)
        hdr.addStretch()

        self.lbl_badge = QLabel("NOMINAL")
        self.lbl_badge.setStyleSheet(f"""
            background: rgba(0, 230, 118, 0.15);
            color: {THEME['status_normal']};
            border: 1px solid {THEME['status_normal']};
            border-radius: 4px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: bold;
        """)
        hdr.addWidget(self.lbl_badge)
        layout.addLayout(hdr)

        # Value & Unit
        val_box = QHBoxLayout()
        self.lbl_val = QLabel("--")
        self.lbl_val.setStyleSheet(f"color: {THEME['text_primary']}; font-size: 24px; font-weight: bold;")
        val_box.addWidget(self.lbl_val)

        if self.unit_text:
            self.lbl_unit = QLabel(self.unit_text)
            self.lbl_unit.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 11px; padding-top: 8px;")
            val_box.addWidget(self.lbl_unit)
        val_box.addStretch()
        layout.addLayout(val_box)

        # Threshold Bounds Reference Text
        bounds_txt = ""
        if self.normal_min is not None and self.normal_max is not None:
            bounds_txt = f"Norm: {self.normal_min:.1f} - {self.normal_max:.1f} {self.unit_text}"
        elif self.normal_min is not None:
            bounds_txt = f"Norm: >= {self.normal_min:.1f} {self.unit_text}"
        elif self.normal_max is not None:
            bounds_txt = f"Norm: <= {self.normal_max:.1f} {self.unit_text}"

        self.lbl_bounds = QLabel(bounds_txt)
        self.lbl_bounds.setStyleSheet(f"color: {THEME['text_muted']}; font-size: 9px;")
        layout.addWidget(self.lbl_bounds)

        # Mini Progress Bar Gauge
        self.bar = QProgressBar()
        self.bar.setFixedHeight(3)
        self.bar.setTextVisible(False)
        self.bar.setRange(0, 100)
        self.bar.setValue(50)
        self.bar.setStyleSheet(f"""
            QProgressBar {{
                background: {THEME['border']};
                border: none;
                border-radius: 1px;
            }}
            QProgressBar::chunk {{
                background: {THEME['accent_cyan']};
                border-radius: 1px;
            }}
        """)
        layout.addWidget(self.bar)

    def set_value(self, val: Optional[float], status: str = "NOMINAL"):
        self.current_value = val
        self.status = status

        if val is None:
            self.lbl_val.setText("DISC")
            self.lbl_badge.setText("DISCONNECTED")
            self._set_status_colors(THEME['status_warning'], "rgba(255, 179, 0, 0.15)")
            self.bar.setValue(0)
            return

        # Format number nicely
        if abs(val) >= 100:
            self.lbl_val.setText(f"{val:.0f}")
        elif abs(val) >= 10:
            self.lbl_val.setText(f"{val:.1f}")
        else:
            self.lbl_val.setText(f"{val:.2f}")

        self.lbl_badge.setText(status)

        if status == "CRITICAL":
            self._set_status_colors(THEME['status_critical'], "rgba(255, 23, 68, 0.20)")
            bar_color = THEME['status_critical']
        elif status == "WARNING":
            self._set_status_colors(THEME['status_warning'], "rgba(255, 179, 0, 0.18)")
            bar_color = THEME['status_warning']
        else:
            self._set_status_colors(THEME['status_normal'], "rgba(0, 230, 118, 0.15)")
            bar_color = THEME['accent_cyan']

        # Update gauge percent
        if self.normal_min is not None and self.normal_max is not None:
            pct = int(((val - self.normal_min) / max(1.0, (self.normal_max - self.normal_min))) * 60 + 20)
            self.bar.setValue(max(5, min(100, pct)))
        else:
            self.bar.setValue(50)

        self.bar.setStyleSheet(f"""
            QProgressBar {{ background: {THEME['border']}; border: none; border-radius: 1px; }}
            QProgressBar::chunk {{ background: {bar_color}; border-radius: 1px; }}
        """)

    def _set_status_colors(self, stroke: str, bg: str):
        self.lbl_badge.setStyleSheet(f"""
            background: {bg};
            color: {stroke};
            border: 1px solid {stroke};
            border-radius: 4px;
            padding: 1px 6px;
            font-size: 9px;
            font-weight: bold;
        """)

    def _update_style(self):
        self.setStyleSheet(f"""
            QFrame#metricCard {{
                background-color: {THEME['bg_card']};
                border: 1px solid {THEME['border']};
                border-radius: 8px;
            }}
            QFrame#metricCard:hover {{
                border-color: {THEME['accent_blue']};
            }}
        """)
