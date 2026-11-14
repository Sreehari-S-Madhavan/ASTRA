"""
ASTRA Seed Data
Populates the database with fictional demo profiles, missions, example workflows,
physician profiles, and illustrative telemetry.
"""
import json
from datetime import datetime, timedelta
from astra.database.db_manager import db_manager


def seed_all_data():
    """Populates all required tables if empty."""
    conn = db_manager.get_connection()
    cursor = conn.cursor()
    
    # 1. Missions
    cursor.execute("SELECT COUNT(*) FROM missions")
    if cursor.fetchone()[0] == 0:
        missions = [
            ("M-ARES5", "ARES-V Mars Exploration", "MTV-1 'Chronos'", "Mars Orbit & Surface", "2026-03-15", 780, "Transit to Mars", "ACTIVE"),
            ("M-ARTEMIS8", "Artemis VIII Deep Base", "Lunar Gateway Shackleton", "Lunar South Pole", "2025-09-01", 180, "Surface Ops", "STANDBY")
        ]
        cursor.executemany(
            "INSERT INTO missions (id, name, spacecraft, destination, launch_date, duration_days, current_phase, status) VALUES (?,?,?,?,?,?,?,?)",
            missions
        )

    # 2. Astronaut Profiles
    cursor.execute("SELECT COUNT(*) FROM astronauts")
    if cursor.fetchone()[0] == 0:
        now_str = datetime.now().isoformat()
        astronauts = [
            (
                "AST-01", "VANCE", "Dr. Alex Vance", 42, "Mission Commander & Geologist", "M-ARES5",
                64.0, 98.5, 116.0, 76.0, 36.6, 14.0,
                "No prior spaceflight contraindications. Mild vestibular sensitivity during initial microgravity transit. Excellent physical conditioning.",
                now_str
            ),
            (
                "AST-02", "ROSTOVA", "Dr. Elena Rostova", 38, "Crew Medical Officer & Astrobiologist", "M-ARES5",
                60.0, 99.0, 112.0, 72.0, 36.5, 13.0,
                "Certified flight surgeon and emergency physician. Regular endurance athlete. Baseline intraocular pressure nominal.",
                now_str
            ),
            (
                "AST-03", "CHEN", "Marcus Chen", 35, "Chief Flight Engineer & EVA Lead", "M-ARES5",
                68.0, 98.0, 120.0, 78.0, 36.7, 15.0,
                "High tolerance to high-G loads. Minor history of lumbar microgravity back elongation discomfort, controlled via resistance exercise.",
                now_str
            )
        ]
        cursor.executemany(
            "INSERT INTO astronauts (id, callsign, name, age, role, mission_id, baseline_hr, baseline_spo2, baseline_sys_bp, baseline_dia_bp, baseline_temp, baseline_resp, medical_summary, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            astronauts
        )

    # 3. Physician Profiles
    cursor.execute("SELECT COUNT(*) FROM physician_profiles")
    if cursor.fetchone()[0] == 0:
        physicians = [
            ("PHY-01", "Dr. Sarah Okonjo, MD, PhD", "Chief Flight Surgeon", "MED-LEAD", "Ground Mission Control (MCC-Houston)", "s.okonjo@ground-med.example", "Aerospace Medicine & Critical Care", "ON_DUTY"),
            ("PHY-02", "Dr. Liam Davies, MD", "Deputy Crew Surgeon", "MED-DEPUTY", "European Space Operations Center (ESOC)", "l.davies@ground-med.example", "Spaceflight Cardiology & Neuro-Vestibular", "ON_DUTY"),
            ("PHY-03", "Dr. Kenji Sato, MD", "Radiation & Toxicology Consultant", "RAD-MED", "JAXA Tsukuba Space Center", "k.sato@ground-med.example", "Radiobiology & Environmental Toxicology", "STANDBY")
        ]
        cursor.executemany(
            "INSERT INTO physician_profiles (id, name, role, callsign, ground_station, email, specialization, availability_status) VALUES (?,?,?,?,?,?,?,?)",
            physicians
        )

    # 4. Fictional example workflows; these are not clinically reviewed or approved.
    cursor.execute("SELECT COUNT(*) FROM medical_protocols")
    if cursor.fetchone()[0] == 0:
        protocols = [
            (
                "PROT-01", "EMERG-HYPOXIA", "Cabin Hypoxia & Suspected Decompression Sickness",
                "Environmental / Respiratory",
                "SpO2 < 90%, sudden cyanosis, cognitive confusion, tachypnea, joint pain (bends), cabin pressure drop.",
                "Immediately seal helmet or don Portable Breathing Apparatus (PBA) providing 100% O2. Verify cabin seal.",
                "1. Connect crew member to 100% normobaric oxygen via high-flow mask.\n2. Recline patient to 30 degrees and restrict movement.\n3. Increase habitat/suit pressure if decompression occurred.\n4. Administer oral fluids if conscious and airway secure.\n5. Continuously record SpO2, heart rate, and respiratory rate.",
                "DO NOT allow active physical exertion. DO NOT delay oxygen administration while troubleshooting cabin telemetry.",
                "SpO2 fails to rise above 92% within 3 minutes of 100% O2, or acute neurological deficits (paralysis, visual field loss, altered consciousness) present.",
                "SpO2, Cabin Pressure (kPa), Heart Rate (bpm), Respiratory Rate (brpm)",
                "ASTRA demo content - not medically approved", "v3.2"
            ),
            (
                "PROT-02", "EMERG-CARDIAC", "Acute Cardiac Episode & Severe Chest Pain",
                "Cardiovascular",
                "Crushing substernal chest pressure, radiation to jaw/left arm, diaphoresis, sudden arrhythmia, syncope.",
                "Halt all physical exercise immediately. Seat patient in semi-Fowler's position. Ensure defibrillator (AED) is on standby.",
                "1. Position crew member upright or semi-recumbent; reduce physical stress.\n2. Apply 3-lead ECG / pulse oximeter for continuous monitoring.\n3. Provide supplemental oxygen if SpO2 < 94%.\n4. Administer 325 mg chewable Aspirin if no allergy or bleeding risk.\n5. Prepare Emergency Medical Kit (EMK) Sublingual Nitroglycerin (0.4 mg) if systolic BP > 100 mmHg.\n6. Transmit priority telemetry packet to Flight Surgeon.",
                "DO NOT administer Nitroglycerin if systolic BP < 100 mmHg or if PDE5 inhibitors used within 48h. DO NOT leave patient unattended.",
                "Persistent pain > 10 minutes, hemodynamic instability (BP < 90/60), new malignant ventricular arrhythmias, or loss of responsiveness.",
                "Heart Rate (bpm), ECG Rhythm, Blood Pressure (mmHg), SpO2 (%)",
                "ASTRA demo content - not medically approved", "v3.1"
            ),
            (
                "PROT-03", "EMERG-SYNCOPE", "Loss of Consciousness & Orthostatic Collapse",
                "Neurological / Cardiovascular",
                "Unresponsiveness, absent verbal response, sudden collapse, transient pallor, weak peripheral pulse.",
                "Check airway, breathing, circulation. Clear immediate surroundings in microgravity to prevent traumatic collision.",
                "1. Secure patient in crew restraint to prevent uncontrolled drift.\n2. Open airway using head-tilt chin-lift (jaw-thrust if trauma suspected).\n3. Confirm carotid/radial pulse and spontaneous respirations.\n4. Elevate lower extremities to facilitate venous return.\n5. Check fingerstick blood glucose and SpO2.\n6. Maintain patient in lateral recovery posture if breathing resumes but consciousness remains blunted.",
                "DO NOT administer oral liquids to an unconscious individual. DO NOT force patient to stand prematurely.",
                "Unresponsiveness lasting > 2 minutes, focal seizure activity, post-ictal confusion > 15 minutes, or trauma sustained during fall/drift.",
                "Heart Rate, SpO2, Blood Glucose, Pupil Reactivity, Blood Pressure",
                "ASTRA demo content - not medically approved", "v2.8"
            ),
            (
                "PROT-04", "EMERG-HEMORRHAGE", "Severe Traumatic Hemorrhage & Laceration",
                "Trauma",
                "Pulsatile or copious blood loss, spreading hematoma, signs of hypovolemic shock (tachycardia > 110, hypotension).",
                "Don sterile PPE. In microgravity, fluid droplets contaminate cabin atmosphere; prepare suction and absorbent gauze.",
                "1. Apply direct firm manual pressure over the bleeding site with sterile hemostatic gauze.\n2. If limb arterial bleeding is uncontrolled by direct pressure, immediately apply Emergency Tourniquet 5-7 cm proximal to wound.\n3. Tighten tourniquet until bleeding halts and distal pulse is abolished; record application time.\n4. Establish IV access and prepare isotonic crystalloid infusion if signs of shock manifest.\n5. Capture airborne fluid with absorbent pads to prevent environmental fouling.",
                "DO NOT apply tourniquet over a joint. DO NOT loosen an applied tourniquet without direct Flight Surgeon authorization.",
                "Failure to control bleeding with direct pressure/tourniquet, systolic BP < 90 mmHg, altered mental state, or tourniquet in place > 60 minutes.",
                "Heart Rate (bpm), Blood Pressure (mmHg), Shock Index, Fluid Volume Administered",
                "ASTRA demo content - not medically approved", "v3.0"
            ),
            (
                "PROT-05", "EMERG-RAD-EVENT", "Acute Solar Particle Event / Severe Radiation Exposure",
                "Environmental / Radiation",
                "Dosimeter alarm > 100 mSv/h, Solar Proton Event (SPE) alert from spacecraft external sensors, nausea, vomiting, erythema.",
                "IMMEDIATE EVACUATION of all crew to the Storm Shelter (central water-shielded habitat core). Seal radiation hatches.",
                "1. Sound Habitat Radiation Alarm; all crew report to Storm Shelter within 3 minutes.\n2. Verify storm shelter water-wall shielding integrity.\n3. Log personal dosimeter readings for each astronaut.\n4. Administer antiemetics (Ondansetron 8 mg IV/oral) at onset of nausea.\n5. Prepare Granulocyte Colony-Stimulating Factor (G-CSF) protocol if cumulative dose exceeds 1.0 Gy.\n6. Maintain continuous communication with Earth Solar Physics & Flight Surgery teams.",
                "DO NOT permit any Extravehicular Activity (EVA) or unshielded module access until Ground declares SPE terminated.",
                "Personal accumulated dose > 500 mSv within 24 hours, persistent vomiting, severe leukopenia, or thermal skin burns.",
                "Dosimeter Cumulative Dose (mSv), Current Rate (µSv/h), CBC / White Blood Count",
                "ASTRA demo content - not medically approved", "v4.0"
            ),
            (
                "PROT-06", "EMERG-TOXIC", "Toxic Atmospheric Contamination / Ammonia / Smoke Ingestion",
                "Environmental / Toxicology",
                "Atmospheric trace gas analyzer alarm, pungent odor, eye irritation, lacrimation, severe coughing, dyspnea, wheezing.",
                "IMMEDIATE donning of Quick-Don Mask with Carbon/HEPA scrubber canister or Emergency PBA. Isolate affected module.",
                "1. Sound Cabin Atmospheric Contamination Alarm; isolate the contaminated module hatch.\n2. All crew don emergency breathing apparatus.\n3. Activate high-capacity Environmental Control and Life Support System (ECLSS) trace contaminant scrubbers.\n4. Rinse exposed eyes/skin with copious saline from emergency wash bottles.\n5. Administer Albuterol / Salbutamol inhaler (4 puffs via spacer) for bronchospasm.\n6. Monitor exhaled CO and cabin hazardous gas concentration levels.",
                "DO NOT open isolated module hatches until atmospheric sample tests confirm toxic agents are below permissible exposure limits (SMAC).",
                "Persistent respiratory distress, refractory bronchospasm, chemical burn to cornea, or loss of consciousness.",
                "Cabin Toxic Gas Concentration (ppm), SpO2, Respiratory Rate, Peak Expiratory Flow",
                "ASTRA demo content - not medically approved", "v3.4"
            ),
            (
                "PROT-07", "EMERG-VESTIBULAR", "Severe Space Adaptation Syndrome & Vestibular Ataxia",
                "Neuro-Vestibular",
                "Intractable vomiting, severe vertigo, spatial disorientation, inability to coordinate hand-eye tasks, pallor, cold sweat.",
                "Fasten astronaut into crew restraint berth to prevent disorientation and injury during vehicle maneuvers.",
                "1. Restrict head and neck movements; avoid sudden rotational pitch/yaw motions.\n2. Administer Promethazine (25-50 mg IM/oral) or Scopolamine transdermal patch as prescribed.\n3. Provide oral electrolyte rehydration solution in small, frequent sips to prevent volume depletion.\n4. Keep ambient cabin illumination subdued; minimize visual clutter.\n5. Monitor for signs of secondary dehydration and electrolyte imbalance.",
                "DO NOT assign safety-critical piloting, robotic arm manipulation, or EVA duties while symptomatic or sedated.",
                "Inability to retain liquids > 24 hours, signs of orthostatic collapse, or persistent vomiting unresponsive to two antiemetic doses.",
                "Hydration Index, Heart Rate, Blood Pressure, Eye Saccade / Nystagmus Score",
                "ASTRA demo content - not medically approved", "v2.5"
            ),
            (
                "PROT-08", "EMERG-SANS", "Acute Spaceflight-Associated Neuro-Ocular Syndrome (SANS) Deterioration",
                "Neuro-Ocular",
                "Sudden progressive visual blurring, scotoma, severe retro-orbital headache, optic disc edema (papilledema), cotton-wool spots.",
                "Dim crew workstation screens. Discontinue prolonged high-concentration close-up visual tasks.",
                "1. Conduct comprehensive funduscopic and visual acuity assessment via onboard ophthalmic diagnostic tools.\n2. Measure intraocular pressure (IOP) using tonometer.\n3. Evaluate neurological status and cranial nerve function.\n4. Apply lower-body negative pressure (LBNP) protocol if approved by Flight Surgeon to redistribute cephalad fluid shifts.\n5. Adjust sleep head-tilt angle and monitor cabin CO2 levels (ensure CO2 < 2.0 mmHg).",
                "DO NOT perform high-intensity Valsalva-inducing resistance exercise until neuro-ophthalmologist evaluation.",
                "Sudden visual acuity loss > 2 lines on Snellen chart, visual field deficit, or intractable headache accompanied by nausea.",
                "Visual Acuity (Snellen), Intraocular Pressure (mmHg), Optical Coherence Tomography (OCT) scan, Head Yaw/Pitch",
                "ASTRA demo content - not medically approved", "v2.2"
            ),
            (
                "PROT-09", "EMERG-HYPOTHERMIA", "Acute Environmental Hypothermia / Thermal Dysregulation",
                "Environmental / Thermal",
                "Core body temp < 35.0°C, uncontrolled shivering, slurred speech, apathy, peripheral cyanosis, bradycardia.",
                "Remove damp garments. Wrap patient in aluminized reflective thermal space blanket within insulated sleeping bag.",
                "1. Insulate patient from cold metal surfaces and thermal bridging in spacecraft hull.\n2. Apply warm packs (chemically activated) to groin, axillae, and torso.\n3. Administer warm, sweetened oral fluids if patient is conscious and swallow reflex is intact.\n4. Warm cabin environmental temperature zone to 24-26°C.\n5. Monitor core temperature continuously via tympanic/axillary sensor.",
                "DO NOT rub frostbitten or cold extremities. DO NOT apply direct scalding heat sources to peripheral limbs.",
                "Core temperature < 34.0°C, cessation of shivering, cardiac dysrhythmias, or deteriorating level of consciousness.",
                "Core Body Temperature (°C), Heart Rate (bpm), ECG Rhythm, Cabin Temperature (°C)",
                "ASTRA demo content - not medically approved", "v2.1"
            ),
            (
                "PROT-10", "EMERG-DEHYDRATION", "Severe Dehydration & Heat Strain Syndrome",
                "Metabolic / Environmental",
                "Tachycardia > 115 bpm at rest, dark concentrated urine, skin turgor loss, sunken eyes, orthostatic dizziness, elevated core temp > 38.5°C.",
                "Cease all physical workouts immediately. Move to high-airflow, ventilated cabin sector.",
                "1. Initiate oral rehydration therapy with WHO-formula oral rehydration salts (ORS) in potable water (1 liter over 2 hours).\n2. If oral intake is not tolerated due to nausea, establish IV line and infuse 0.9% Normal Saline at 150 mL/h.\n3. Active evaporative cooling with moist towels and localized fan airflow.\n4. Measure urine specific gravity and volume output.\n5. Re-check vital signs every 15 minutes until hemodynamic stability is restored.",
                "DO NOT administer cold bolus water too rapidly to avoid water intoxication or gastric distress.",
                "Signs of acute heat stroke (core temp > 40°C, altered mental status, delirium, anhidrosis) or persistent hypotension (systolic BP < 85 mmHg).",
                "Core Temperature (°C), Heart Rate (bpm), Blood Pressure (mmHg), Hydration Index (%)",
                "ASTRA demo content - not medically approved", "v2.9"
            )
        ]
        cursor.executemany(
            "INSERT INTO medical_protocols (id, code, title, category, observable_signs, immediate_safety, first_aid_steps, contraindications, escalation_criteria, required_telemetry, approved_by, version) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            protocols
        )

    # 5. Baseline Environmental Readings
    cursor.execute("SELECT COUNT(*) FROM environmental_readings")
    if cursor.fetchone()[0] == 0:
        base_time = datetime.now() - timedelta(hours=6)
        env_rows = []
        for i in range(12):
            t = (base_time + timedelta(minutes=30 * i)).isoformat()
            env_rows.append((
                t, 21.0, 1.8, 101.3, 22.2, 48.0, 24.5, "NOMINAL", "All life support loops nominal. Trace contaminant scrubbers running normally."
            ))
        cursor.executemany(
            "INSERT INTO environmental_readings (timestamp, o2_percent, co2_mmhg, cabin_pressure_kpa, cabin_temp_c, humidity_pct, radiation_rate_usv_h, system_status, notes) VALUES (?,?,?,?,?,?,?,?,?)",
            env_rows
        )

    # 6. Baseline Health Readings (fictional history for AST-01, AST-02, AST-03)
    cursor.execute("SELECT COUNT(*) FROM health_readings")
    if cursor.fetchone()[0] == 0:
        base_time = datetime.now() - timedelta(hours=8)
        health_rows = []
        for i in range(16):
            t = (base_time + timedelta(minutes=30 * i)).isoformat()
            # AST-01
            health_rows.append((
                "AST-01", t, 65.0 + (i % 3), 98.2, 116.0, 76.0, 36.6, 14.0, 88.0, 7.5, 2.0, "SIMULATED", "VALID", 1, "Routine baseline"
            ))
            # AST-02
            health_rows.append((
                "AST-02", t, 61.0 + (i % 2), 99.0, 112.0, 72.0, 36.5, 13.0, 92.0, 8.0, 1.5, "SIMULATED", "VALID", 1, "Routine baseline"
            ))
            # AST-03
            health_rows.append((
                "AST-03", t, 68.0 + (i % 4), 98.0, 120.0, 78.0, 36.7, 15.0, 85.0, 7.0, 2.5, "SIMULATED", "VALID", 1, "Routine baseline"
            ))
        cursor.executemany(
            "INSERT INTO health_readings (astronaut_id, timestamp, heart_rate, spo2, sys_bp, dia_bp, temperature, respiratory_rate, hydration_index, sleep_hours, fatigue_score, source_type, validity_status, sensor_connected, notes) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            health_rows
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    seed_all_data()
    print("Seed data successfully populated.")
