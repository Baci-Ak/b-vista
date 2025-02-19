import os
import socket
import threading
import time
import pandas as pd
from flask_socketio import SocketIO

# ✅ Global variables for managing sessions
ACTIVE_HOST = "127.0.0.1"
ACTIVE_PORT = None
SERVER_THREAD = None
socketio = None  # ✅ Real-time updates

# ✅ Define a safe port range for the backend
MIN_PORT = 40000
MAX_PORT = 49000

# ✅ Storage for active dataset sessions
sessions = {}  # {session_id: {"df": DataFrame, "port": int, "name": str}}


def find_free_port():
    """Find an available port automatically."""
    for port in range(MIN_PORT, MAX_PORT):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind((ACTIVE_HOST, port))
                return port
            except OSError:
                continue
    raise RuntimeError("No available ports in the defined range.")


def start_server(port=None):
    """Start the backend Flask server dynamically in the background."""
    global ACTIVE_PORT, SERVER_THREAD, socketio

    if port is None:
        port = find_free_port()

    ACTIVE_PORT = port

    from app import app, socketio  # ✅ Import here to prevent circular imports

    def run():
        """Run Flask server in the background silently (no logs)."""
        socketio.run(app, host=ACTIVE_HOST, port=ACTIVE_PORT, allow_unsafe_werkzeug=True, log_output=False)

    # ✅ Run the server in a separate thread (silent mode)
    SERVER_THREAD = threading.Thread(target=run, daemon=True)
    SERVER_THREAD.start()
    time.sleep(2)  # ✅ Allow time for the server to initialize


def load_dataframe(df, name=None):
    """Load a Pandas DataFrame into memory with a unique session ID."""
    global ACTIVE_PORT, sessions

    if ACTIVE_PORT is None:
        start_server()  # ✅ Start server if not already running

    session_id = str(len(sessions) + 1)  # ✅ Unique session ID
    dataset_name = name or f"Dataset_{session_id}"  # ✅ Auto-generate dataset name

    # ✅ Store dataset in memory
    sessions[session_id] = {
        "df": df,
        "port": ACTIVE_PORT,
        "name": dataset_name
    }

    # ✅ Emit live updates (silent)
    if socketio:
        socketio.emit("data_update", {
            "session_id": session_id,
            "data": df.to_dict(orient="records"),
            "name": dataset_name
        }, namespace='/')

    return {"url": f"http://{ACTIVE_HOST}:{ACTIVE_PORT}", "session_id": session_id, "name": dataset_name}


def get_available_sessions():
    """Retrieve all active dataset sessions."""
    return {
        session_id: {"name": session["name"], "port": session["port"]}
        for session_id, session in sessions.items()
    }


def get_dataset(session_id):
    """Retrieve a dataset by session ID."""
    return sessions.get(session_id, {}).get("df")


def switch_dataset(session_id):
    """Switch to a different dataset session by session ID."""
    if session_id not in sessions:
        return None
    return {
        "session_id": session_id,
        "data": sessions[session_id]["df"].to_dict(orient="records"),
        "name": sessions[session_id]["name"]
    }
