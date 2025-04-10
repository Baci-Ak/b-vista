import subprocess
import time
import requests
import os
import sys
import platform
import logging
from importlib.resources import files


logger = logging.getLogger(__name__)

API_URL = "http://127.0.0.1:5050"
_backend_started = False  # Prevent re-entry


def is_backend_running() -> bool:
    try:
        response = requests.get(f"{API_URL}/api/get_sessions", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _validate_environment():
    if sys.version_info < (3, 6):
        return "⚠️ B-Vista requires Python 3.6 or higher."
    if "dev" in platform.python_implementation().lower():
        return "⚠️ Running on a development build of Python. Consider switching to a stable release."
    return None


def start_backend(silent: bool = True):
    global _backend_started

    if _backend_started or is_backend_running():
        return

    _backend_started = True

    warning = _validate_environment()
    if warning and not silent:
        logging.warning(warning)

    # Dynamically locate backend/app.py
    try:
        from importlib.resources import files
        backend_path = str(files("bvista").joinpath("backend", "app.py"))
    except Exception:
        raise FileNotFoundError("❌ Could not resolve path to backend/app.py using importlib.resources")

    if not os.path.exists(backend_path):
        raise FileNotFoundError(f"❌ Could not find backend script at {backend_path}")

    try:
        subprocess.Popen(
            [sys.executable, backend_path],
            stdout=subprocess.DEVNULL if silent else None,
            stderr=subprocess.DEVNULL if silent else None,
            start_new_session=True
        )
    except Exception as e:
        raise RuntimeError(f"❌ Failed to launch backend: {e}")

    for _ in range(15):
        if is_backend_running():
            return
        time.sleep(1)

    raise RuntimeError("❌ Backend failed to start within the expected time.")
