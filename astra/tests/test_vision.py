"""
ASTRA Automated Unit Tests: Computer Vision & Screening Engine
"""
import unittest
import numpy as np
from astra.cv.camera_manager import CameraQualityMetrics
from astra.cv.vision_engine import VisionEngine, vision_engine
from astra.cv.visual_tests import tracking_test, reaction_test


class TestVision(unittest.TestCase):

    def test_camera_quality_metrics(self):
        dark_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        metrics = CameraQualityMetrics.evaluate(dark_frame)
        self.assertEqual(metrics["brightness"], 0.0)
        self.assertEqual(metrics["status"], "LOW_LIGHT")

        t_frame = np.full((480, 640, 3), 128, dtype=np.uint8)
        metrics_nominal = CameraQualityMetrics.evaluate(t_frame)
        self.assertEqual(metrics_nominal["brightness"], 128.0)

    def test_vision_engine_frame_processing(self):
        frame = np.full((480, 640, 3), 120, dtype=np.uint8)
        p_frame, results = vision_engine.process_frame(frame, draw_overlays=False)
        self.assertIn("ear", results)
        self.assertIn("blink_count", results)
        self.assertIn("head_pitch", results)
        self.assertIn("head_yaw", results)
        self.assertIn("facial_asymmetry_pct", results)

    def test_no_face_does_not_report_face_measurements(self):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        _, results = VisionEngine().process_frame(frame, draw_overlays=False)

        self.assertFalse(results["face_detected"])
        self.assertIsNone(results["face_bbox"])
        self.assertIsNone(results["ear"])
        self.assertIsNone(results["blink_rate_per_min"])
        self.assertIsNone(results["facial_asymmetry_pct"])

    def test_guided_visual_tracking_test(self):
        tracking_test.start()
        self.assertTrue(tracking_test.is_active)
        pt = tracking_test.get_target_position(640, 480)
        self.assertEqual(len(pt), 2)
        tracking_test.record_sample(pt, (pt[0] + 5, pt[1] + 5))
        res = tracking_test.stop()
        self.assertEqual(res["test_type"], "GUIDED_EYE_TRACKING")
        self.assertGreater(res["tracking_error_px"], 0)

    def test_guided_visual_tracking_without_face_samples_is_incomplete(self):
        tracking_test.start()
        result = tracking_test.stop()

        self.assertEqual(result["status"], "INCOMPLETE")
        self.assertIsNone(result["tracking_error_px"])

    def test_visual_reaction_test(self):
        reaction_test.start_trial()
        self.assertTrue(reaction_test.is_waiting_stimulus)
        reaction_test.stimulus_active = True
        reaction_test.trigger_time = 100.0
        latency = reaction_test.record_response()
        self.assertIsNotNone(latency)


if __name__ == "__main__":
    unittest.main()
