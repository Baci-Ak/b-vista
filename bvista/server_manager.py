import subprocess
import time
import requests
import os
import sys

API_URL = "http://127.0.0.1:5050"

def is_backend_running():
    """Check if the backend server is running."""
    try:
        response = requests.get(f"{API_URL}/api/get_sessions", timeout=2)
        return response.status_code == 200
    except requests.RequestException:
        return False

def start_backend():
    """Start the backend server automatically if not already running."""
    if is_backend_running():
        print("✅ B-Vista backend is already running.")
        return

    #print("🚀 Starting B-Vista backend...")
    backend_path = os.path.join(os.path.dirname(__file__), "../backend/app.py")

    process = subprocess.Popen(
        [sys.executable, backend_path],  # Use the exact Python interpreter running bvista
        stdout=subprocess.DEVNULL,  # ✅ Suppress logs
        stderr=subprocess.DEVNULL,  # ✅ Suppress errors
    )

    # Wait until the backend is up
    for _ in range(15):  # Wait for up to 15 seconds
        if is_backend_running():
            #print("✅ B-Vista backend is running.")
            return
        time.sleep(1)

    # If backend doesn't start, print error logs
    stdout, stderr = process.communicate()
    print("❌ Failed to start the backend.")
    print("🔴 Backend Logs (stdout):")
    print(stdout)
    print("🔴 Backend Logs (stderr):")
    print(stderr)