# ✅ WebSocket Event Handlers for Real-time Updates
import logging
from flask_socketio import emit, join_room, leave_room, rooms
from .socket_manager import socketio
from models.data_manager import get_available_sessions

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

@socketio.on("connect")
def handle_connect():
    """Handle new client connections."""
    logging.info("✅ Client connected to WebSocket.")
    emit("connection_success", {"message": "Connected to WebSocket server!"})


@socketio.on("join_session")
def handle_join_session(data):
    """Allow clients to join a dataset session."""
    session_id = data.get("session_id")

    # ✅ Check if session exists
    if session_id not in get_available_sessions():
        logging.warning(f"⚠️ Attempt to join non-existent session {session_id}")
        emit("error", {"message": f"Session {session_id} not found."})
        return

    join_room(session_id)
    logging.info(f"✅ Client joined session {session_id}")
    emit("session_joined", {"message": f"Joined session {session_id}"}, room=session_id)


@socketio.on("leave_session")
def handle_leave_session(data):
    """Allow clients to leave a session."""
    session_id = data.get("session_id")

    leave_room(session_id)
    logging.info(f"✅ Client left session {session_id}")
    emit("session_left", {"message": f"Left session {session_id}"}, room=session_id)


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnections."""
    for room in rooms():
        leave_room(room)  # ✅ Leave all rooms
    logging.info("❌ Client disconnected from WebSocket.")
    emit("disconnection_success", {"message": "Disconnected from WebSocket server"})
