# ✅ API Routes for Dataset Management
from flask import Blueprint, request, jsonify
import pandas as pd
import logging
from models.data_manager import add_session, get_session, delete_session, get_available_sessions
import os 

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

        # ✅ Automatically determine dataset name (remove .csv from dropdown name)
        name = request.form.get("name", file.filename)
        name = os.path.splitext(name)[0]  # Remove file extension

        # ✅ Try reading the file as CSV first, fallback to Excel
        try:
            df = pd.read_csv(file)
        except Exception:
            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                logging.error(f"❌ Unsupported or invalid file format: {file.filename} - {e}")
                return jsonify({"error": "Invalid or unsupported file format"}), 400

        # ✅ Add dataset session
        add_session(session_id, df, name)

        logging.info(f"✅ Dataset uploaded successfully under session {session_id} ({name})")
        return jsonify({"message": "File uploaded", "session_id": session_id, "name": name}), 200

    except Exception as e:
        logging.exception("❌ Error uploading dataset.")
        return jsonify({"error": str(e)}), 500



# ✅ Route: Retrieve dataset
@data_routes.route("/session/<session_id>", methods=["GET"])
def get_data(session_id):
    """Retrieve dataset by session ID."""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]  # ✅ Extract DataFrame
    return jsonify({
        "session_id": session_id,
        "name": session["name"],
        "data": df.to_dict(orient="records"),
        "columns": [{"field": col, "headerName": col} for col in df.columns],
        "total_rows": df.shape[0],  # ✅ Send total row count
        "total_columns": df.shape[1]  # ✅ Send total column count
    }), 200



# ✅ Route: Get all available dataset sessions
@data_routes.route("/sessions", methods=["GET"])
def get_sessions():
    """Retrieve a list of all active dataset sessions."""
    return jsonify({"sessions": get_available_sessions()}), 200


# ✅ Route: Delete dataset
@data_routes.route("/delete/<session_id>", methods=["DELETE"])
def delete_data(session_id):
    """Delete a dataset session."""
    delete_session(session_id)
    return jsonify({"message": f"Session {session_id} deleted"}), 200
