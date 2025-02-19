# manages dataset sessions and handles server startup
import os
import threading
import pandas as pd
import logging
from flask import jsonify

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ In-memory storage for dataset sessions
sessions = {}


def add_session(session_id, data):
    """Add a new dataset session."""
    if session_id in sessions:
        logging.warning(f"⚠️ Session {session_id} already exists. Overwriting data.")
    sessions[session_id] = data
    logging.info(f"✅ Session {session_id} added.")


def get_session(session_id):
    """Retrieve dataset session by ID."""
    if session_id not in sessions:
        logging.error(f"❌ Session {session_id} not found.")
        return jsonify({"error": "Session not found"}), 404
    return sessions[session_id]


def get_available_sessions():
    """Return all active session IDs."""
    return list(sessions.keys())


def delete_session(session_id):
    """Delete a dataset session."""
    if session_id in sessions:
        del sessions[session_id]
        logging.info(f"🗑️ Session {session_id} deleted.")
    else:
        logging.warning(f"⚠️ Attempted to delete non-existent session {session_id}.")


def start_server():
    """Initialize backend services."""
    logging.info("🔥 Initializing dataset session manager...")
    if not os.path.exists("datasets"):
        os.makedirs("datasets")  # ✅ Ensure dataset storage exists
    logging.info("✅ Dataset directory verified.")

    # ✅ Start background cleanup process
    threading.Thread(target=session_cleanup, daemon=True).start()


def session_cleanup():
    """Background task to clean up inactive sessions."""
    logging.info("🔄 Session cleanup process started.")
    while True:
        inactive_sessions = [sid for sid, data in sessions.items() if data.empty]
        for sid in inactive_sessions:
            delete_session(sid)


# ✅ Ensure the module is correctly initialized
start_server()
