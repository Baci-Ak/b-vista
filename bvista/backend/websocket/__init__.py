# This file initializes the WebSocket module and ensures it integrates with the Flask app
from .socket_manager import socketio
from .event_handlers import handle_connect, handle_join_session, handle_leave_session, handle_disconnect

def register_websocket(app):
    """Attach the WebSocket to the Flask app."""
    socketio.init_app(app, cors_allowed_origins="*")  # ✅ Ensure WebSocket is initialized
