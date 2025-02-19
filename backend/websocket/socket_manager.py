# This file manages real-time WebSocket connections using Flask-SocketIO, enabling live data updates.

from flask_socketio import SocketIO

# ✅ Initialize SocketIO
socketio = SocketIO(cors_allowed_origins="*")

def broadcast_update(session_id, data):
    """Send real-time updates to clients."""
    socketio.emit("update_data", {"session_id": session_id, "data": data})
