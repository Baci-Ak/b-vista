from flask import Blueprint, request, jsonify
import pandas as pd
from models.data_manager import (
    load_dataframe,
    get_available_sessions,
    get_dataset,
    switch_dataset
)

data_routes = Blueprint("data_routes", __name__)

@data_routes.route("/load_data", methods=["POST"])
def load_data():
    """Load a dataset into memory, assign a session ID, and return session details."""
    try:
        data = request.json
        if not data or "data" not in data:
            return jsonify({"status": "error", "message": "No data received"}), 400

        df = pd.DataFrame(data["data"])
        dataset_name = data.get("name", None)  # Keep dataset name optional
        session_info = load_dataframe(df, name=dataset_name)

        return jsonify({
            "status": "success",
            "message": "Data loaded successfully!",
            "session_id": session_info["session_id"],
            "url": session_info["url"]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@data_routes.route("/get_sessions", methods=["GET"])
def get_sessions():
    """Retrieve a list of all active dataset sessions."""
    try:
        sessions = get_available_sessions()
        return jsonify({"status": "success", "sessions": sessions}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@data_routes.route("/get_data/<session_id>", methods=["GET"])
def get_data(session_id):
    """Retrieve stored dataset by session ID."""
    try:
        df = get_dataset(session_id)
        if df is None:
            return jsonify({"status": "error", "message": "Session ID not found"}), 404

        return jsonify({
            "status": "success",
            "session_id": session_id,
            "data": df.to_dict(orient="records"),
            "columns": [{"headerName": col, "field": col} for col in df.columns]
        }), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@data_routes.route("/switch_dataset", methods=["POST"])
def switch_data():
    """Switch to a different dataset by session ID."""
    try:
        data = request.json
        session_id = data.get("session_id")
        if not session_id:
            return jsonify({"status": "error", "message": "Session ID is required"}), 400

        new_session = switch_dataset(session_id)
        if not new_session:
            return jsonify({"status": "error", "message": "Session ID not found"}), 404

        return jsonify({"status": "success", "session": new_session}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
