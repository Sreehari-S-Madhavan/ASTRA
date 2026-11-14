"""
ASTRA Virtual Space Companion ("Astraea")
An original procedural vector-animated celestial companion creature rendered using PySide6 QPainter.
Features 7 distinct emotional/operational states, floating orbital dynamics, and speech synthesis hooks.
"""
import math
import random
from typing import Optional
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton
from PySide6.QtCore import Qt, QTimer, QRectF, QPointF
from PySide6.QtGui import QPainter, QColor, QRadialGradient, QPen, QBrush, QFont, QPainterPath
from astra.core.event_bus import bus


class CompanionMood:
    IDLE = "idle"
    TALKING = "talking"
    LISTENING = "listening"
    THINKING = "thinking"
    HAPPY = "happy"
    CONCERNED = "concerned"
    EMERGENCY = "emergency"


class CompanionAvatar(QWidget):
    """Vector procedural canvas rendering the animated cosmic companion creature."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(180, 180)
        self.mood = CompanionMood.IDLE
        self.anim_frame = 0.0
        self.blink_alpha = 1.0
        self.is_blinking = False
        self.blink_counter = 0

        # Animation loop (30 FPS)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._animate)
        self.timer.start(33)

    def set_mood(self, mood: str):
        self.mood = mood.lower()
        self.update()

    def _animate(self):
        self.anim_frame += 0.08
        if self.anim_frame > 2 * math.pi * 100:
            self.anim_frame = 0.0

        # Autonomous blinking
        self.blink_counter += 1
        if self.blink_counter > 90 and not self.is_blinking:
            if random.random() < 0.1:
                self.is_blinking = True
                self.blink_counter = 0
        elif self.is_blinking:
            self.blink_alpha -= 0.25
            if self.blink_alpha <= 0.0:
                self.blink_alpha = 1.0
                self.is_blinking = False

        self.update()

    def mousePressEvent(self, event):
        """Interacting with Astraea triggers a cheerful or helpful response."""
        mood_cycle = [CompanionMood.HAPPY, CompanionMood.THINKING, CompanionMood.LISTENING, CompanionMood.IDLE]
        next_mood = random.choice(mood_cycle)
        self.set_mood(next_mood)
        hints = [
            "Astraea online! All life-support and biometric telemetry loops are syncing.",
            "Touch sensor detected. How are you feeling today, Commander?",
            "Analyzing cabin telemetry: Oxygen partial pressure and shielding look solid.",
            "I'm ready to assist with your routine visual screening whenever you are."
        ]
        bus.companion_message_requested.emit(random.choice(hints), next_mood)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        cx, cy = w / 2.0, h / 2.0

        # Floating vertical bounce
        float_y = math.sin(self.anim_frame * 1.5) * 6.0
        cy += float_y

        # Select color palette based on mood
        if self.mood == CompanionMood.EMERGENCY:
            core_color = QColor(255, 23, 68)
            glow_color = QColor(255, 23, 68, 80)
            halo_color = QColor(255, 82, 82, 140)
        elif self.mood == CompanionMood.CONCERNED:
            core_color = QColor(255, 179, 0)
            glow_color = QColor(255, 179, 0, 70)
            halo_color = QColor(255, 213, 79, 120)
        elif self.mood == CompanionMood.HAPPY:
            core_color = QColor(0, 230, 118)
            glow_color = QColor(0, 230, 118, 80)
            halo_color = QColor(105, 240, 174, 140)
        elif self.mood == CompanionMood.THINKING:
            core_color = QColor(124, 77, 255)
            glow_color = QColor(124, 77, 255, 80)
            halo_color = QColor(179, 136, 255, 140)
        else:  # IDLE, TALKING, LISTENING
            core_color = QColor(0, 229, 255)
            glow_color = QColor(0, 229, 255, 75)
            halo_color = QColor(128, 222, 234, 130)

        # 1. Outer Bioluminescent Energy Aura
        pulse_r = 55.0 + math.sin(self.anim_frame * 2.5) * 4.0
        glow_grad = QRadialGradient(cx, cy, pulse_r * 1.6)
        glow_grad.setColorAt(0.0, glow_color)
        glow_grad.setColorAt(0.7, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 20))
        glow_grad.setColorAt(1.0, QColor(0, 0, 0, 0))
        painter.setBrush(QBrush(glow_grad))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(cx, cy), pulse_r * 1.6, pulse_r * 1.6)

        # 2. Orbital Particle Rings
        painter.save()
        painter.translate(cx, cy)
        rot_angle = (self.anim_frame * 20.0) % 360
        painter.rotate(rot_angle)
        orbit_pen = QPen(halo_color, 1.5, Qt.DashLine)
        painter.setPen(orbit_pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QPointF(0, 0), pulse_r * 1.25, pulse_r * 0.45)
        # Orbiting micro-satellite mote
        painter.setBrush(QBrush(core_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPointF(pulse_r * 1.25, 0), 3.5, 3.5)
        painter.restore()

        # 3. Main Creature Core Body (Celestial sphere)
        body_grad = QRadialGradient(cx - 10, cy - 10, pulse_r)
        body_grad.setColorAt(0.0, QColor(255, 255, 255, 240))
        body_grad.setColorAt(0.3, core_color)
        body_grad.setColorAt(0.85, QColor(core_color.red() // 2, core_color.green() // 2, core_color.blue() // 2, 220))
        body_grad.setColorAt(1.0, QColor(10, 14, 23, 200))
        painter.setBrush(QBrush(body_grad))
        painter.setPen(QPen(core_color, 1.5))
        painter.drawEllipse(QPointF(cx, cy), pulse_r, pulse_r)

        # 4. Luminescent Sensory Antennae / Ears
        ant_left_x = cx - 28
        ant_right_x = cx + 28
        ant_top_y = cy - pulse_r - 8 - math.sin(self.anim_frame * 3.0) * 3.0
        painter.setPen(QPen(core_color, 2.5))
        painter.drawLine(QPointF(cx - 18, cy - pulse_r + 10), QPointF(ant_left_x, ant_top_y))
        painter.drawLine(QPointF(cx + 18, cy - pulse_r + 10), QPointF(ant_right_x, ant_top_y))
        # Antenna tips
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.drawEllipse(QPointF(ant_left_x, ant_top_y), 4.0, 4.0)
        painter.drawEllipse(QPointF(ant_right_x, ant_top_y), 4.0, 4.0)

        # 5. Expressive Eyes
        eye_y = cy - 6
        eye_offset = 16.0
        eye_rx = 7.0
        eye_ry = 9.0 * self.blink_alpha

        painter.setBrush(QBrush(QColor(10, 14, 23)))
        painter.setPen(Qt.NoPen)
        if self.blink_alpha > 0.1:
            painter.drawEllipse(QPointF(cx - eye_offset, eye_y), eye_rx, eye_ry)
            painter.drawEllipse(QPointF(cx + eye_offset, eye_y), eye_rx, eye_ry)

            # Pupil sparkle
            painter.setBrush(QBrush(QColor(255, 255, 255)))
            painter.drawEllipse(QPointF(cx - eye_offset - 2, eye_y - 2), 2.5, 2.5)
            painter.drawEllipse(QPointF(cx + eye_offset - 2, eye_y - 2), 2.5, 2.5)
        else:
            # Closed happy eye arcs
            painter.setPen(QPen(QColor(255, 255, 255), 2.0))
            painter.drawArc(QRectF(cx - eye_offset - 6, eye_y - 3, 12, 6), 0, 180 * 16)
            painter.drawArc(QRectF(cx + eye_offset - 6, eye_y - 3, 12, 6), 0, 180 * 16)

        # 6. Mouth / Vocalization Pulse
        painter.setPen(QPen(QColor(255, 255, 255), 1.8))
        mouth_y = cy + 16
        if self.mood == CompanionMood.TALKING:
            mouth_open = abs(math.sin(self.anim_frame * 6.0)) * 6.0 + 2.0
            painter.setBrush(QBrush(QColor(10, 14, 23)))
            painter.drawEllipse(QPointF(cx, mouth_y), 5.0, mouth_open)
        elif self.mood == CompanionMood.HAPPY:
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(QRectF(cx - 7, mouth_y - 4, 14, 8), 180 * 16, 180 * 16)
        elif self.mood == CompanionMood.CONCERNED or self.mood == CompanionMood.EMERGENCY:
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(QRectF(cx - 6, mouth_y, 12, 6), 0, 180 * 16)
        else:
            # Idle small gentle smile
            painter.setBrush(Qt.NoBrush)
            painter.drawArc(QRectF(cx - 5, mouth_y - 2, 10, 6), 200 * 16, 140 * 16)


class CompanionWidget(QWidget):
    """Complete Companion panel integrating the avatar, dialog balloon, and audio controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        # Header Title
        title_box = QHBoxLayout()
        self.title_lbl = QLabel("VIRTUAL COMPANION • ASTRAEA")
        self.title_lbl.setStyleSheet("color: #00E5FF; font-weight: bold; font-size: 11px; letter-spacing: 1px;")
        title_box.addWidget(self.title_lbl)
        title_box.addStretch()

        self.mute_btn = QPushButton("MUTE")
        self.mute_btn.setCheckable(True)
        self.mute_btn.setStyleSheet("""
            QPushButton { background: #182338; color: #94A3B8; border: 1px solid #283958; border-radius: 4px; padding: 2px 8px; font-size: 10px; }
            QPushButton:checked { background: #FF1744; color: white; border-color: #FF1744; }
        """)
        title_box.addWidget(self.mute_btn)
        layout.addLayout(title_box)

        # Centered Avatar
        avatar_box = QHBoxLayout()
        avatar_box.addStretch()
        self.avatar = CompanionAvatar(self)
        avatar_box.addWidget(self.avatar)
        avatar_box.addStretch()
        layout.addLayout(avatar_box)

        # Speech Dialogue Balloon
        self.speech_bubble = QLabel("Greetings, Commander. I am Astraea, your onboard medical companion. Monitoring telemetry is nominal.")
        self.speech_bubble.setWordWrap(True)
        self.speech_bubble.setStyleSheet("""
            QLabel {
                background: #182338;
                color: #F0F4FC;
                border: 1px solid #283958;
                border-left: 3px solid #00E5FF;
                border-radius: 8px;
                padding: 10px 12px;
                font-size: 11px;
                line-height: 15px;
            }
        """)
        layout.addWidget(self.speech_bubble)

        # Interactive quick prompts
        btn_layout = QHBoxLayout()
        btn_check = QPushButton("Check Status")
        btn_screen = QPushButton("Visual Screen")
        btn_relax = QPushButton("Wellness")

        for b in [btn_check, btn_screen, btn_relax]:
            b.setStyleSheet("""
                QPushButton { background: #121A2A; color: #94A3B8; border: 1px solid #283958; border-radius: 4px; padding: 4px 6px; font-size: 10px; }
                QPushButton:hover { background: #22314E; color: #00E5FF; border-color: #00E5FF; }
            """)
            btn_layout.addWidget(b)

        btn_check.clicked.connect(lambda: self.say("All life-support ECLSS loops are operating within nominal green boundaries.", CompanionMood.HAPPY))
        btn_screen.clicked.connect(lambda: self.say("Ready for camera assessment. Look straight into the webcam to measure gaze, blinks, and motor alignment.", CompanionMood.LISTENING))
        btn_relax.clicked.connect(lambda: self.say("Remember to take a 10-minute visual relaxation break. Look out the cupola or focus on a distant landmark.", CompanionMood.TALKING))

        layout.addLayout(btn_layout)

        # Connect to central event bus
        bus.companion_message_requested.connect(self.say)

    def say(self, message: str, mood: str = CompanionMood.TALKING):
        """Displays message and updates creature mood."""
        self.avatar.set_mood(mood)
        self.speech_bubble.setText(message)
        
        # Audio voice synthesis if not muted
        if not self.mute_btn.isChecked():
            from astra.companion.voice_engine import voice_engine
            voice_engine.speak(message)
