# ✅ WebSocket Manager for Real-time Updates
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room
from models.data_manager import get_session, delete_session, get_available_sessions



# ✅ Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def broadcast_update(session_id, df):
    """Send real-time dataset updates to clients."""
    data = df.to_dict(orient="records")
    columns = [{"field": col, "headerName": col} for col in df.columns]
    
    socketio.emit("update_data", {"session_id": session_id, "data": data, "columns": columns}, room=session_id)

@socketio.on("connect")
def handle_connect():
    """Handle new client connections."""
    emit("connection_success", {"message": "Connected to WebSocket server!"})

@socketio.on("join_session")
def handle_join_session(data):
    """Allow clients to join a dataset session only if it's active."""
    session_id = data.get("session_id")

    # ✅ Check if session exists and is not expired
    session = get_session(session_id)
    if session is None:
        emit("session_expired", {"message": f"Session {session_id} has expired and is no longer available."})
        return

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

def cleanup_expired_websocket_sessions():
    """Remove expired sessions from WebSocket and notify clients."""
    expired_sessions = [sid for sid in get_available_sessions() if get_session(sid) is None]

    for sid in expired_sessions:
        delete_session(sid)  # ✅ Remove from memory
        socketio.emit("session_expired", {"message": f"Session {sid} has expired."}, room=sid)
        close_room(sid)  # ✅ Force clients to disconnect from expired session




@socketio.on("update_cell")
def handle_update_cell(data):
    """Broadcast real-time cell updates to all connected users."""
    session_id = data.get("session_id")
    if not session_id:
        return

    # ✅ Send only the modified cell
    socketio.emit("update_cell", data, room=session_id)
