# ✅ Manages dataset sessions and handles server startup
import os
import time
import threading
import pandas as pd
import logging

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ In-memory storage for dataset sessions
sessions = {}


def add_session(session_id, data, name="Untitled Dataset"):
    """Add a new dataset session."""
    if session_id in sessions:
        logging.warning(f"⚠️ Session {session_id} already exists. Overwriting data.")
    
    # ✅ Store session with metadata
    sessions[session_id] = {
        "df": data,
        "name": name,
        "created_at": time.time(),
    }
    logging.info(f"✅ Session {session_id} added ({name}).")



def get_session(session_id):
    """Retrieve dataset session by ID."""
    session = sessions.get(session_id)
    if session is None:
        logging.error(f"❌ Session {session_id} not found.")
        return None  # No JSON response here, handled at API level
    return session


def get_available_sessions():
    """Return a dictionary of active session IDs and metadata."""
    return {sid: {"name": s["name"], "created_at": s["created_at"]} for sid, s in sessions.items()}


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
    os.makedirs("datasets", exist_ok=True)  # ✅ Ensure dataset storage exists
    logging.info("✅ Dataset directory verified.")

    # ✅ Start background cleanup process
    threading.Thread(target=session_cleanup, daemon=True).start()


def session_cleanup():
    """Background task to clean up inactive sessions."""
    logging.info("🔄 Session cleanup process started.")
    while True:
        time.sleep(30)  # ✅ Cleanup every 30 seconds (prevents CPU overload)
        inactive_sessions = [sid for sid, data in sessions.items() if data["df"].empty]
        for sid in inactive_sessions:
            delete_session(sid)
