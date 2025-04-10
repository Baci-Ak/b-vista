# ✅ Manages dataset sessions and handles server startup
import os
import time
import threading
import pandas as pd
import logging
from collections import OrderedDict  # ✅ Faster lookup for active sessions

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ In-memory storage for dataset sessions
sessions = OrderedDict()

# ✅ Set session expiration time (default: 1 hour)
SESSION_EXPIRATION_TIME = int(os.getenv("SESSION_EXPIRATION_TIME", 3600))  # 3600 seconds = 1 hour

def add_session(session_id, data, name="Untitled Dataset"):
    """Add a new dataset session."""
    if session_id in sessions:
        logging.warning(f"⚠️ Session {session_id} already exists. Overwriting data.")

    # ✅ Store session with metadata and timestamp
    sessions[session_id] = {
        "df": data,
        "name": name,
        "created_at": time.time(),  # Store session creation time
    }
    logging.info(f"✅ Session {session_id} added ({name}).")

def get_session(session_id):
    """Retrieve dataset session by ID, ensuring it has not expired."""
    cleanup_expired_sessions()  # ✅ Ensure expired sessions are removed before fetching data

    session = sessions.get(session_id)
    if session is None:
        logging.error(f"❌ Session {session_id} not found or expired.")
        return None
    return session

def get_available_sessions():
    """Return a dictionary of active session IDs and metadata."""
    cleanup_expired_sessions()  # ✅ Ensure only active sessions are returned
    return {sid: {"name": s["name"], "created_at": s["created_at"]} for sid, s in sessions.items()}

def delete_session(session_id):
    """Delete a dataset session."""
    if session_id in sessions:
        del sessions[session_id]
        logging.info(f"🗑️ Session {session_id} deleted.")
    else:
        logging.warning(f"⚠️ Attempted to delete non-existent session {session_id}.")

def cleanup_expired_sessions():
    """Automatically remove sessions that have expired."""
    current_time = time.time()
    expired_sessions = [sid for sid, data in sessions.items() if (current_time - data["created_at"]) > SESSION_EXPIRATION_TIME]

    for sid in expired_sessions:
        delete_session(sid)
        logging.info(f"⏳ Session {sid} expired and was deleted.")

def start_server():
    """Initialize backend services."""
    logging.info("🔥 Initializing dataset session manager...")
    os.makedirs("datasets", exist_ok=True)  # ✅ Ensure dataset storage exists
    logging.info("✅ Dataset directory verified.")

    # ✅ Start background cleanup process
    threading.Thread(target=session_cleanup, daemon=True).start()

def session_cleanup():
    """Background task to clean up inactive and expired sessions."""
    logging.info("🔄 Session cleanup process started.")
    while True:
        time.sleep(30)  # ✅ Cleanup every 30 seconds (prevents CPU overload)
        cleanup_expired_sessions()  # ✅ Remove expired sessions

        # ✅ Remove empty DataFrames (this was already implemented)
        inactive_sessions = [sid for sid, data in sessions.items() if data["df"].empty]
        for sid in inactive_sessions:
            delete_session(sid)
