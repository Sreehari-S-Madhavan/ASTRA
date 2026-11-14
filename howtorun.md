# ASTRA — Setup and Launch

## Requirements

- Python 3.10 or newer
- A webcam for physical camera screening
- Windows, Linux, or macOS

## Install

From the project root, create and activate a virtual environment.

**Windows PowerShell**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**Git Bash, Linux, or macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Run

From the project root:

```bash
python run_tests.py
python astra/main.py
```

Or launch with the project script. It works from any current directory and prefers the project-local `.venv`:

```bash
bash /path/to/astra/run_astra.sh
```

On Windows, run the launcher from Git Bash or WSL. In the Camera Screening page, choose the camera rotation and mirroring that match your camera.

## Voice and data notes

- Windows microphone commands use the local Windows Speech Recognition engine; audio is not sent to an online service. Typed commands are available on all platforms.
- ASTRA is a software demo, not a medical device or source of medical advice. Do not use its sample workflows for real patient care or use the app with real health data.
- Local SQLite databases and generated reports are intentionally excluded from Git by `.gitignore`.