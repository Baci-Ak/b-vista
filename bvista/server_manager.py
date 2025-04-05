import subprocess
import time
import requests
import os
import sys
import platform

API_URL = "http://127.0.0.1:5050"
_backend_started = False  # prevent re-entry


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
    """
    Start the backend server if not already running.

    Args:
        silent (bool): Suppress console output. Default is True (no logs).
    """
    global _backend_started
    if _backend_started or is_backend_running():
        return

    _backend_started = True

    warning = _validate_environment()
    if warning and not silent:
        print(warning)

    backend_entry = "-m"
    backend_target = "backend.app"
    process = None

    try:
        process = subprocess.Popen(
            [sys.executable, backend_entry, backend_target],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )
    except Exception:
        app_path = os.path.join(os.path.dirname(__file__), "..", "backend", "app.py")
        process = subprocess.Popen(
            [sys.executable, app_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

    for _ in range(15):
        if is_backend_running():
            return
        time.sleep(1)

    stdout, stderr = process.communicate()
    if not silent:
        print("❌ Failed to start the backend.")
        print("🔴 Backend Logs (stdout):")
        print(stdout.decode() if stdout else "None")
        print("🔴 Backend Logs (stderr):")
        print(stderr.decode() if stderr else "None")
