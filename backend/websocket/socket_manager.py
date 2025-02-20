# ✅ WebSocket Manager for Real-time Updates
from flask_socketio import SocketIO, emit, join_room, leave_room

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
    """Allow clients to join a dataset session."""
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
