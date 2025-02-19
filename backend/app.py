import sys
import os
import socket
import pandas as pd
from flask import Flask, send_from_directory, jsonify, request
from flask_socketio import SocketIO
from flask_cors import CORS

# ✅ Ensure the backend path is accessible
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# ✅ Import session manager
from models.data_manager import sessions, start_server, get_available_sessions
from routes.data_routes import data_routes  # ✅ Import the API routes

# ✅ Set up the Flask app
app = Flask(__name__, static_folder="../frontend/bvista-frontend/build", static_url_path="/")
CORS(app)  # ✅ Allow frontend to communicate with the backend
socketio = SocketIO(app, cors_allowed_origins="*")  # ✅ Enable real-time updates

# ✅ Register API routes
app.register_blueprint(data_routes, url_prefix="/api")


@app.route("/")
def serve_react():
    """Serve the React frontend."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    """Serve static files for the React frontend."""
    return send_from_directory(app.static_folder, path)


@app.route("/healthcheck")
def healthcheck():
    """Check if the backend is running."""
    return jsonify({"status": "running"}), 200


@app.route("/latest_session", methods=["GET"])
def latest_session():
    """Retrieve the most recent session ID."""
    if not sessions:
        return jsonify({"error": "No sessions available"}), 404

    latest_session_id = max(sessions.keys(), key=int)
    return jsonify({"session_id": latest_session_id})


@app.route("/api/get_sessions", methods=["GET"])
def get_sessions():
    """Retrieve a list of all active dataset sessions."""
    return jsonify({"sessions": get_available_sessions()}), 200


def is_port_in_use(port):
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0


if __name__ == "__main__":
    # ✅ Ensure backend runs silently in the background
    start_server()
