"""
ASTRA Central Event Bus
Decouples application components (vision, telemetry, risk assessment, emergency, companion).
Supports both Qt Signal/Slot binding and lightweight callback subscriptions.
"""
from typing import Callable, Dict, List, Any
from PySide6.QtCore import QObject, Signal


class EventBus(QObject):
    """Qt-compatible thread-safe Event Bus."""
    
    # Core system signals
    vitals_updated = Signal(dict)           # Emitted when new physiological readings arrive
    environment_updated = Signal(dict)      # Emitted when environmental readings arrive
    hazard_detected = Signal(dict)          # Emitted when a spaceflight hazard event is flagged
    alert_generated = Signal(dict)          # Emitted when health risk engine issues LOW/MOD/CRIT alert
    emergency_activated = Signal(dict)      # Emitted when emergency state is activated
    emergency_resolved = Signal(dict)       # Emitted when emergency state is resolved
    camera_assessment_completed = Signal(dict) # Emitted when a visual screening test completes
    companion_message_requested = Signal(str, str) # (text, mood) to trigger companion response
    report_queued = Signal(dict)            # Emitted when medical report is created/queued
    message_status_changed = Signal(dict)   # Emitted when ground comm status updates (Delivered/Ack)
    active_astronaut_changed = Signal(str)  # Emitted when selected astronaut changes (e.g. AST-01)

    def __init__(self):
        super().__init__()
        self._raw_subscribers: Dict[str, List[Callable[[Any], None]]] = {}

    def subscribe(self, event_name: str, callback: Callable[[Any], None]):
        """Subscribe raw Python callback to named event."""
        if event_name not in self._raw_subscribers:
            self._raw_subscribers[event_name] = []
        self._raw_subscribers[event_name].append(callback)

    def emit_event(self, event_name: str, payload: Any):
        """Dispatches event to raw subscribers."""
        if event_name in self._raw_subscribers:
            for cb in self._raw_subscribers[event_name]:
                try:
                    cb(payload)
                except Exception as e:
                    print(f"Error in subscriber callback for {event_name}: {e}")


# Global EventBus singleton
bus = EventBus()
