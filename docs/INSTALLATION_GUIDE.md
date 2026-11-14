# ASTRA: Installation & Execution Guide

## 1. System Requirements
- **Operating System**: Windows 10/11 (64-bit), macOS 12+, or Ubuntu 22.04+
- **Processor**: Standard x86_64 / ARM64 dual-core processor (no dedicated GPU required)
- **RAM**: 4 GB minimum (8 GB recommended)
- **Webcam**: Standard integrated laptop camera or external USB video class (UVC) webcam
- **Python**: Python 3.10, 3.11, 3.12, 3.13, or 3.14

## 2. Dependencies
ASTRA is built with minimal dependencies:
- **PySide6**: High-performance Qt desktop application framework, vector rendering, and native PDF writer.
- **NumPy**: Fast matrix operations and vector geometry.
- **OpenCV (`opencv-python`)**: Computer vision face detection, landmark cascades, and solvePnP.
- **FastAPI / Uvicorn** (optional): Ground Station telecommunications simulation receiver.
- **pyttsx3** (optional): Text-to-speech audio feedback.

## 3. Installation Steps

### Step 1: Clone or Open Workspace
```bash
cd astra
```

### Step 2: Install Required Packages
```bash
pip install PySide6 numpy opencv-python
```

*(Note: If OpenCV is not installed or physical camera is unplugged, ASTRA automatically switches to its built-in procedural synthetic astronaut feed, so the entire workstation remains 100% operational!)*

### Step 3: Run the Verification Test Suite
```bash
python run_tests.py
```
Expected output:
```
Ran 18 tests in 0.585s
OK
```

### Step 4: Launch the Medical Workstation
```bash
python astra/main.py
```

### Optional: Launch Remote Ground Station Server
To simulate external Ground Mission Control in another terminal:
```bash
python astra/physician/server.py
```
This runs the Ground Telemetry Station on `http://127.0.0.1:8765`.
