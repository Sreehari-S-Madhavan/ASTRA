"""
ASTRA Voice Engine
Provides offline speech synthesis and Windows-native offline voice commands.
"""
import base64
import os
import queue
import shutil
import subprocess
import threading
from typing import Optional

from PySide6.QtCore import QObject, QThread, Signal


POWERSHELL = shutil.which("powershell.exe") or shutil.which("powershell")


def _encode_powershell(script: str) -> str:
    return base64.b64encode(script.encode("utf-16le")).decode("ascii")


class SpeechWorker(threading.Thread):
    """Processes speech synthesis requests without blocking the GUI."""

    def __init__(self, report_error):
        super().__init__(daemon=True)
        self.queue = queue.Queue()
        self.engine = None
        self.report_error = report_error
        self.use_system_speech = os.name == "nt" and POWERSHELL is not None

    def run(self):
        while True:
            text = self.queue.get()
            try:
                if text is None:
                    return
                if self.use_system_speech:
                    self._speak_with_system_speech(text)
                else:
                    self._speak_with_pyttsx3(text)
            finally:
                self.queue.task_done()

    def _speak_with_system_speech(self, text: str):
        escaped_text = text.replace("'", "''")
        script = (
            "Add-Type -AssemblyName System.Speech; "
            "$speaker = New-Object System.Speech.Synthesis.SpeechSynthesizer; "
            f"$speaker.Speak('{escaped_text}'); "
            "$speaker.Dispose()"
        )
        try:
            subprocess.run(
                [POWERSHELL, "-NoProfile", "-NonInteractive", "-EncodedCommand", _encode_powershell(script)],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except (OSError, subprocess.SubprocessError) as error:
            self.report_error(f"Offline speech synthesis failed: {error}")

    def _speak_with_pyttsx3(self, text: str):
        try:
            if self.engine is None:
                import pyttsx3

                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", 165)
                self.engine.setProperty("volume", 0.85)
            self.engine.say(text)
            self.engine.runAndWait()
        except (ImportError, OSError, RuntimeError) as error:
            self.report_error(f"Speech synthesis is unavailable: {error}")

    def enqueue(self, text: str):
        self.queue.put(text)


class SpeechRecognitionWorker(QThread):
    """Captures and transcribes one utterance with Windows' offline recognizer."""

    transcription_ready = Signal(str)
    error = Signal(str)

    def __init__(self):
        super().__init__()
        self.process: Optional[subprocess.Popen] = None

    def run(self):
        if os.name != "nt" or POWERSHELL is None:
            self.error.emit("Offline microphone commands require Windows Speech Recognition.")
            return

        script = r"""
$ErrorActionPreference = 'Stop'
$engine = $null
try {
    Add-Type -AssemblyName System.Speech
    $engine = New-Object System.Speech.Recognition.SpeechRecognitionEngine
    $engine.LoadGrammar((New-Object System.Speech.Recognition.DictationGrammar))
    $engine.SetInputToDefaultAudioDevice()
    $result = $engine.Recognize([TimeSpan]::FromSeconds(10))
    if ($null -eq $result) {
        exit 2
    }
    [Console]::Out.Write($result.Text)
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
} finally {
    if ($null -ne $engine) {
        $engine.Dispose()
    }
}
"""
        try:
            self.process = subprocess.Popen(
                [POWERSHELL, "-NoProfile", "-NonInteractive", "-EncodedCommand", _encode_powershell(script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            process = self.process
            stdout, stderr = process.communicate(timeout=15)
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.communicate()
            self.error.emit("Voice command timed out. Click the microphone and try again.")
            return
        except OSError as error:
            self.error.emit(f"Could not start offline voice recognition: {error}")
            return
        finally:
            self.process = None

        if return_code == 2:
            self.error.emit("No speech was detected. Check the microphone and try again.")
            return
        if return_code != 0:
            self.error.emit(f"Offline voice recognition failed: {stderr.strip() or 'Speech recognizer returned an error.'}")
        elif stdout.strip():
            self.transcription_ready.emit(stdout.strip())
        else:
            self.error.emit("No speech was detected. Check the microphone and try again.")

    def stop(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()


class VoiceEngine(QObject):
    """Parses text or offline microphone commands for the companion UI."""

    command_recognized = Signal(str, str)
    voice_error = Signal(str)
    listening_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = SpeechWorker(self.voice_error.emit)
        self.worker.start()
        self._recognition_worker: Optional[SpeechRecognitionWorker] = None
        self.is_muted = False

    def set_muted(self, muted: bool):
        self.is_muted = muted

    def speak(self, text: str):
        """Asynchronously plays a spoken response unless the assistant is muted."""
        if not self.is_muted and text:
            self.worker.enqueue(text)

    def start_listening(self) -> bool:
        """Starts one local microphone capture; never sends audio to a network service."""
        if self._recognition_worker and self._recognition_worker.isRunning():
            return False

        self._recognition_worker = SpeechRecognitionWorker()
        self._recognition_worker.transcription_ready.connect(self.process_command)
        self._recognition_worker.error.connect(self.voice_error.emit)
        self._recognition_worker.finished.connect(self._on_recognition_finished)
        self._recognition_worker.start()
        self.listening_changed.emit(True)
        return True

    def toggle_listening(self):
        if self._recognition_worker and self._recognition_worker.isRunning():
            self.stop_listening()
        else:
            self.start_listening()

    def stop_listening(self):
        worker = self._recognition_worker
        if worker and worker.isRunning():
            worker.stop()
            worker.wait(2000)
            if not worker.isRunning():
                self._on_recognition_finished()

    def _on_recognition_finished(self):
        self._recognition_worker = None
        self.listening_changed.emit(False)

    def process_command(self, raw_text: str) -> tuple[Optional[str], str]:
        """Maps natural language command phrases to system intents."""
        cmd = raw_text.strip().lower()

        if "check my health" in cmd or "health status" in cmd or "vitals" in cmd:
            intent = "NAV_HEALTH"
            resp = "Navigating to Physiological Health Monitoring dashboard."
        elif "start health assessment" in cmd or "run eye screening" in cmd or "camera screening" in cmd or "eye tracking" in cmd:
            intent = "NAV_CAMERA"
            resp = "Launching Camera-Based Visual Screening Suite."
        elif "show environmental status" in cmd or "environment" in cmd or "eclss" in cmd or "cabin" in cmd:
            intent = "NAV_HAZARDS"
            resp = "Displaying Spaceflight Environmental & Hazard Monitoring panel."
        elif "explain this alert" in cmd or "risk assessment" in cmd or "why alert" in cmd:
            intent = "NAV_RISK"
            resp = "Opening Health Risk Assessment transparent indicator breakdown."
        elif "open emergency assistance" in cmd or "emergency" in cmd or "help" in cmd or "sos" in cmd:
            intent = "NAV_EMERGENCY"
            resp = "ACTIVATING EMERGENCY RESPONSE CONSOLE IMMEDIATELY."
        elif "generate medical report" in cmd or "create report" in cmd or "pdf" in cmd:
            intent = "ACTION_GEN_REPORT"
            resp = "Generating comprehensive PDF medical dossier."
        elif "contact physician" in cmd or "call ground" in cmd or "flight surgeon" in cmd:
            intent = "NAV_COMMUNICATION"
            resp = "Opening Ground Mission Control physician communication uplink."
        elif "show my health history" in cmd or "history" in cmd:
            intent = "NAV_REPORTS"
            resp = "Opening historical medical records and dossiers."
        else:
            intent = "UNKNOWN"
            resp = f"Astraea heard: '{raw_text}'. You can say 'Check health', 'Run eye screening', 'Show environment', or 'Open emergency'."

        self.command_recognized.emit(intent, resp)
        return intent, resp


voice_engine = VoiceEngine()
