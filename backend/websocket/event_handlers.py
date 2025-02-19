# This file handles WebSocket events such as client connections and data updates.
from flask_socketio import emit, join_room, leave_room
from .socket_manager import socketio

@socketio.on("connect")
def handle_connect():
    """Handle new client connections."""
    emit("connection_success", {"message": "Connected to WebSocket server!"})

@socketio.on("join_session")
def handle_join_session(data):
    """Allow clients to join a session for real-time updates."""
    session_id = data.get("session_id")
    join_room(session_id)
    emit("session_joined", {"message": f"Joined session {session_id}"}, room=session_id)

@socketio.on("leave_session")
def handle_leave_session(data):
    """Allow clients to leave a session."""
    session_id = data.get("session_id")
    leave_room(session_id)
    emit("session_left", {"message": f"Left session {session_id}"}, room=session_id)

@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnections."""
    emit("disconnection_success", {"message": "Disconnected from WebSocket server"})
