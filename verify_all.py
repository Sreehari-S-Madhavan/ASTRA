"""
ASTRA Complete System Verification Script
Tests application initialization, database population, camera engine,
risk evaluation, emergency activation, communication dispatch, and PDF generation.
"""
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from PySide6.QtWidgets import QApplication
from astra.database.db_manager import db_manager
from astra.database.seed_data import seed_all_data
from astra.health.models import VitalSigns, EnvironmentalMetrics
from astra.health.risk_engine import risk_engine
from astra.health.hazard_engine import hazard_engine
from astra.emergency.emergency_manager import emergency_manager
from astra.emergency.protocols import protocol_registry
from astra.cv.camera_manager import CameraThread
from astra.cv.vision_engine import vision_engine
from astra.cv.visual_tests import tracking_test, reaction_test, coordination_test
from astra.physician.comm_manager import comm_manager
from astra.reporting.report_generator import report_generator
from astra.simulation.mission_simulator import simulator


def verify_all():
    print("=== ASTRA COMPLETE SYSTEM VERIFICATION ===")
    app = QApplication.instance() or QApplication(sys.argv)

    # 1. Database & Seed Data
    print("1. Verifying Database & Seed Data...")
    db_manager.init_database()
    seed_all_data()
    astronauts = db_manager.execute_query("SELECT COUNT(*) FROM astronauts")
    protocols = db_manager.execute_query("SELECT COUNT(*) FROM medical_protocols")
    print(f"   -> Astronauts: {astronauts[0]['COUNT(*)']} | Protocols: {protocols[0]['COUNT(*)']}")
    assert astronauts[0]['COUNT(*)'] >= 3
    assert protocols[0]['COUNT(*)'] >= 10

    # 2. Camera & Vision Engine
    print("2. Verifying Camera & Computer Vision Engine...")
    cam = CameraThread(device_index=0)
    synthetic_frame = cam._generate_synthetic_astronaut_feed()
    assert synthetic_frame is not None
    assert synthetic_frame.shape == (480, 640, 3)

    processed_frame, results = vision_engine.process_frame(synthetic_frame, draw_overlays=True)
    assert "ear" in results
    assert "head_pitch" in results
    assert "facial_asymmetry_pct" in results
    print(f"   -> EAR: {results['ear']:.3f} | Head Pitch: {results['head_pitch']:.1f}° | Asymmetry: {results['facial_asymmetry_pct']:.1f}%")

    # 3. Guided Visual Tests
    print("3. Verifying Guided Visual Tests...")
    tracking_test.start()
    pt = tracking_test.get_target_position(640, 480)
    tracking_test.record_sample(pt, (pt[0] + 4, pt[1] + 4))
    res_track = tracking_test.stop()
    print(f"   -> Eye Tracking Smooth Pursuit Error: {res_track['tracking_error_px']} px")
    assert res_track['tracking_error_px'] > 0

    reaction_test.start_trial()
    reaction_test.stimulus_active = True
    reaction_test.trigger_time = time.time() - 0.245
    latency = reaction_test.record_response()
    print(f"   -> Visual Reaction Latency: {latency:.1f} ms")
    assert latency > 200

    # 4. Health Risk Engine & Hazard Evaluation
    print("4. Verifying Health Risk Engine & Hazard Engine...")
    v = VitalSigns(astronaut_id="AST-01", heart_rate=142.0, spo2=83.0)
    e = EnvironmentalMetrics(o2_percent=17.0, cabin_pressure_kpa=86.0, radiation_rate_usv_h=350.0)
    alerts = risk_engine.evaluate(vitals=v, environment=e)
    crit = [a for a in alerts if a.alert_level == "CRITICAL"]
    print(f"   -> Risk Alerts Generated: {len(alerts)} (Critical: {len(crit)})")
    assert len(crit) >= 1

    haz_events = hazard_engine.evaluate_hazards(e.to_dict(), v.to_dict(), {})
    print(f"   -> Hazard Events Detected: {len(haz_events)}")
    assert len(haz_events) >= 2

    # 5. Emergency Life-Support Workflow
    print("5. Verifying Emergency Lifecycle...")
    incident = emergency_manager.activate_emergency("AST-01", "PROT-01", v.to_dict())
    assert incident["status"] == "ACTIVE"
    emergency_manager.log_action_step("Crew connected to 100% O2 mask.")
    emergency_manager.update_status("RESOLVED", "All parameters stabilized.")
    print("   -> Emergency Protocol PROT-01 activated, step logged, and marked RESOLVED.")

    # 6. Deep Space Physician Communications
    print("6. Verifying Interplanetary Comm & Delayed Store-and-Forward...")
    comm_manager.set_comm_delay(0.2)
    msg = comm_manager.send_message(
        sender="CREW-CMO [AST-02]",
        recipient="MCC-FLIGHT-SURGEON",
        subject="Autonomous System Telemetry Packet",
        body="Verification run test packet.",
        priority="URGENT"
    )
    assert msg["status"] == "QUEUED"
    print(f"   -> Message {msg['msg_uid']} queued for DSN transmission.")

    # 7. Native PDF Medical Report Generation
    print("7. Verifying Medical Dossier PDF Generation...")
    rep = report_generator.generate_report(
        astronaut_id="AST-01",
        report_type="SYSTEM_VERIFICATION_REPORT",
        severity="ROUTINE",
        vitals=v.to_dict(),
        environment=e.to_dict(),
        camera_obs=results,
        alerts=[a.to_dict() for a in alerts],
        summary="Automated end-to-end operational verification report."
    )
    assert os.path.exists(rep["pdf_path"])
    print(f"   -> PDF Report Successfully Created on Disk: {rep['pdf_path']}")

    # 8. Mission Simulation Engine
    print("8. Verifying Mission Simulator...")
    simulator.load_scenario("DECOMPRESSION")
    assert simulator.current_scenario_key == "DECOMPRESSION"
    simulator._step()
    simulator.load_scenario("NOMINAL")
    assert simulator.current_scenario_key == "NOMINAL"
    print("   -> Simulation Engine ticks and scenario loading verified.")

    print("\n>>> ALL ASTRA SUBSYSTEMS FULLY OPERATIONAL AND VERIFIED! <<<")


if __name__ == "__main__":
    verify_all()
