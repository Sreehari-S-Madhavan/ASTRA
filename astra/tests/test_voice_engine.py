"""Automated tests for offline voice command processing."""
import unittest
from unittest.mock import Mock, patch

from astra.companion import voice_engine as voice_module
from astra.companion.voice_engine import SpeechRecognitionWorker, VoiceEngine


class TestVoiceEngine(unittest.TestCase):

    def test_speech_recognition_emits_local_transcription(self):
        process = Mock()
        process.communicate.return_value = ("check my health", "")
        process.returncode = 0
        transcriptions = []
        worker = SpeechRecognitionWorker()
        worker.transcription_ready.connect(transcriptions.append)

        with patch.object(voice_module.os, "name", "nt"), \
                patch.object(voice_module, "POWERSHELL", "powershell.exe"), \
                patch.object(voice_module.subprocess, "Popen", return_value=process) as popen:
            worker.run()

        self.assertEqual(transcriptions, ["check my health"])
        self.assertIn("-EncodedCommand", popen.call_args.args[0])

    def test_no_speech_reports_error(self):
        process = Mock()
        process.communicate.return_value = ("", "")
        process.returncode = 2
        errors = []
        worker = SpeechRecognitionWorker()
        worker.error.connect(errors.append)

        with patch.object(voice_module.os, "name", "nt"), \
                patch.object(voice_module, "POWERSHELL", "powershell.exe"), \
                patch.object(voice_module.subprocess, "Popen", return_value=process):
            worker.run()

        self.assertEqual(len(errors), 1)
        self.assertIn("No speech was detected", errors[0])

    def test_typed_command_mapping(self):
        engine = VoiceEngine()
        try:
            intent, _ = engine.process_command("run eye screening")
            self.assertEqual(intent, "NAV_CAMERA")
        finally:
            engine.worker.queue.put(None)


if __name__ == "__main__":
    unittest.main()
