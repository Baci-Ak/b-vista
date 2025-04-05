import os
import sys
import socket
import logging
from pathlib import Path
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO

# ✅ Set up logging (silent unless specified)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Ensure backend modules are importable
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# ✅ Import app utilities
from models.data_manager import sessions, get_available_sessions
from routes.data_routes import data_routes

# ✅ Frontend path
FRONTEND_BUILD_PATH = Path(__file__).resolve().parents[1] / "frontend" / "build"

# ✅ Flask app config
app = Flask(__name__, static_folder=str(FRONTEND_BUILD_PATH), static_url_path="/")
CORS(app, resources={r"/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*")

# ✅ Register API routes
app.register_blueprint(data_routes, url_prefix="/api")

# ✅ React routes
@app.route("/")
def serve_react():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# ✅ Healthcheck
@app.route("/healthcheck")
def healthcheck():
    return jsonify({"status": "running"}), 200

@app.route("/latest_session", methods=["GET"])
def latest_session():
    if not sessions:
        return jsonify({"error": "No sessions available"}), 404
    latest_session_id = max(sessions.keys(), key=int)
    return jsonify({"session_id": latest_session_id})

@app.route("/api/get_sessions", methods=["GET"])
def get_sessions():
    return jsonify({"sessions": get_available_sessions()}), 200

# ✅ Utility to check port
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", port)) == 0

# ✅ Only run manually for development
if __name__ == "__main__":
    debug_mode = os.getenv("BVISTA_DEBUG", "true").lower() == "true"
    logging.info("🔧 Running B-Vista Backend locally on port 5050...")
    socketio.run(app, host="0.0.0.0", port=5050, debug=debug_mode, allow_unsafe_werkzeug=True)
