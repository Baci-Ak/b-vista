# This file handles API requests for dataset management
from flask import Blueprint, request, jsonify
import pandas as pd
import logging
from models.data_manager import add_session, get_session, delete_session

# ✅ Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Define Blueprint for API routes
data_routes = Blueprint("data_routes", __name__)

# ✅ Route: Upload dataset
@data_routes.route("/upload", methods=["POST"])
def upload_data():
    """Upload a dataset and create a session."""
    try:
        if "file" not in request.files:
            logging.error("❌ No file provided in the request.")
            return jsonify({"error": "No file provided"}), 400

        file = request.files["file"]
        session_id = request.form.get("session_id", "default")

        if not file.filename.endswith((".csv", ".xlsx")):
            logging.error(f"❌ Unsupported file format: {file.filename}")
            return jsonify({"error": "Only CSV and Excel files are supported"}), 400

        # ✅ Read dataset into DataFrame
        df = pd.read_csv(file) if file.filename.endswith(".csv") else pd.read_excel(file)
        add_session(session_id, df)

        logging.info(f"✅ Dataset uploaded successfully under session {session_id}")
        return jsonify({"message": "File uploaded", "session_id": session_id}), 200

    except Exception as e:
        logging.exception("❌ Error uploading dataset.")
        return jsonify({"error": str(e)}), 500


# ✅ Route: Retrieve dataset
@data_routes.route("/session/<session_id>", methods=["GET"])
def get_data(session_id):
    """Retrieve dataset by session ID."""
    data = get_session(session_id)
    if isinstance(data, tuple):  # If error response is returned
        return data
    return jsonify({"session_id": session_id, "data": data.to_dict()}), 200


# ✅ Route: Delete dataset
@data_routes.route("/delete/<session_id>", methods=["DELETE"])
def delete_data(session_id):
    """Delete a dataset session."""
    delete_session(session_id)
    return jsonify({"message": f"Session {session_id} deleted"}), 200
