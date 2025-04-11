import subprocess
import time
import requests
import os
import sys
import platform
import logging
from importlib.resources import files



def _in_docker():
    """Detect if running inside a Docker container."""
    path = "/proc/1/cgroup"
    return (
        os.path.exists("/.dockerenv") or
        (os.path.isfile(path) and any("docker" in line for line in open(path)))
    )



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
    
    # Skip auto-start if inside Docker (Docker handles this)
    if _in_docker():
        logger.info("🛑 Detected Docker environment — skipping backend auto-start.")
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

    # ✅ Smart + flexible wait logic
    timeout = 30  # total seconds to wait
    interval = 0.5  # check twice per second
    start = time.time()

    while time.time() - start < timeout:
        if is_backend_running():
            if not silent:
                logger.info(f"✅ Backend started after {round(time.time() - start, 1)} seconds.")
            return
        time.sleep(interval)

    raise RuntimeError("❌ Backend failed to start within the expected time.")
