# ✅ API Routes for Dataset Management
from flask import Blueprint, request, jsonify
import pandas as pd
import logging
import json
from models.data_manager import add_session, get_session, delete_session, get_available_sessions
import os 
import pickle
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
            df = pickle.loads(file.read())
        except Exception:
            try:
                df = pd.read_pickle('file.pkl')
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
# ✅ Route: Retrieve dataset
@data_routes.route("/session/<session_id>", methods=["GET"])
def get_data(session_id):
    """Retrieve dataset by session ID, ensuring all missing values are JSON-safe."""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"].copy()  # ✅ Work with a COPY

    logging.info(f"📊 DataFrame types in session {session_id}:\n{df.dtypes}")

    # ✅ Get the correct data types for each column
    dtype_mapping = df.dtypes.apply(lambda x: str(x)).to_dict()

    # ✅ Convert datetime columns to string format "%Y-%m-%d %H:%M:%S"
    for col in df.select_dtypes(include=['datetime64']).columns:
        df[col] = df[col].apply(lambda x: x.strftime("%Y-%m-%d %H:%M:%S") if pd.notna(x) else None)

    # ✅ Convert timedelta columns to human-readable format
    for col in df.select_dtypes(include=['timedelta64']).columns:
        df[col] = df[col].apply(lambda x: str(x) if pd.notna(x) else None)

    # ✅ Convert boolean columns to `True`/`False` instead of UI checkboxes
    for col in df.select_dtypes(include=['bool']).columns:
        df[col] = df[col].astype(bool).replace({True: "True", False: "False", None: None})

    # ✅ Convert categorical columns to string
    for col in df.select_dtypes(include=['category']).columns:
        df[col] = df[col].astype(str).replace("nan", None)


    # ✅ Convert numerical missing values (NaN) to None, preserving dtype
    for col in df.select_dtypes(include=['float64', 'int64']).columns:
        df[col] = df[col].apply(lambda x: x if pd.notna(x) else None)


    # ✅ Convert object columns (mixed types, JSON, lists, dicts)
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x) if pd.notna(x) else None)

    # ✅ Convert DataFrame to JSON-safe dictionary
    data_json_safe = df.to_dict(orient="records")

    # ✅ Replace NaN values with None for JSON compatibility
    for row in data_json_safe:
        for col, value in row.items():
            if pd.isna(value):
                row[col] = None

    return jsonify({
        "session_id": session_id,
        "name": session["name"],
        "data": data_json_safe,
        "columns": [
            {
                "field": col,
                "headerName": col,
                "dataType": dtype_mapping[col],
            }
            for col in df.columns
        ],
        "total_rows": df.shape[0],
        "total_columns": df.shape[1]
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

# ✅ Route: Remove duplicate rows from dataset
@data_routes.route("/remove_duplicates/<session_id>", methods=["GET", "POST"])
def remove_duplicates(session_id):
    """Remove duplicate rows from the dataset and return count."""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]  # ✅ Get the DataFrame
    original_size = len(df)
    df_cleaned = df.drop_duplicates(keep="first")  # ✅ Remove duplicates

    duplicates_removed = original_size - len(df_cleaned)

    # ✅ Update the session with the cleaned dataset
    session["df"] = df_cleaned

    return jsonify({
        "message": f"Removed {duplicates_removed} duplicate rows",
        "total_duplicates_removed": duplicates_removed,
        "new_total_rows": len(df_cleaned),
    }), 200


# ✅ Route: Update a specific cell in the dataset

@data_routes.route("/update_cell/<session_id>", methods=["POST"])
def update_cell(session_id):
    """Update a specific cell in the dataset and broadcast the change via WebSocket."""
    try:
        data = request.json
        column = data.get("column")
        row_index = data.get("row_index")
        new_value = data.get("new_value")

        # ✅ Retrieve the dataset session
        session = get_session(session_id)
        if session is None:
            return jsonify({"error": "Session not found"}), 404

        df = session["df"]  # ✅ Get the DataFrame

        # ✅ Ensure the column exists
        if column not in df.columns:
            return jsonify({"error": "Invalid column"}), 400

        # ✅ Ensure row index is within range
        if row_index < 0 or row_index >= len(df):
            return jsonify({"error": "Invalid row index"}), 400

        # ✅ Update the DataFrame
        df.at[row_index, column] = new_value

        # ✅ Broadcast the update to all WebSocket clients
        from websocket.socket_manager import socketio
        socketio.emit("update_data", {"session_id": session_id, "data": df.to_dict(orient="records")})

        return jsonify({"message": "Cell updated successfully"}), 200

    except Exception as e:
        logging.exception("❌ Error updating cell.")
        return jsonify({"error": str(e)}), 500
    
# ✅ Route: Detect duplicates

@data_routes.route("/detect_duplicates/<session_id>", methods=["GET"])
def detect_duplicates(session_id):
    """Detect duplicate rows in the dataset without modifying it."""
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]  # ✅ Get the DataFrame

    # ✅ Identify duplicate rows (excluding the first occurrence)
    duplicate_mask = df.duplicated(keep=False)  # Marks all occurrences of duplicates

    # ✅ Count only the duplicates that would be removed
    duplicates_to_remove = df.duplicated(keep="first").sum()

    return jsonify({
        "message": f"✅ {duplicates_to_remove} duplicate rows detected.",
        "total_duplicates": int(duplicates_to_remove),  # Ensure integer type
    }), 200



@data_routes.route("/convert_datatype/<session_id>", methods=["POST"])
def convert_datatype(session_id):
    """Convert the data type of a specified column and persist it in the session."""
    try:
        data = request.json
        column = data.get("column")
        new_type = data.get("new_type")

        session = get_session(session_id)
        if session is None:
            logging.error(f"❌ Session {session_id} not found.")
            return jsonify({"error": "Session not found"}), 404

        df = session["df"].copy()  # ✅ Work with a COPY

        if column not in df.columns:
            logging.error(f"❌ Column {column} not found in session {session_id}.")
            return jsonify({"error": "Column not found"}), 400

        logging.info(f"🔄 Converting column '{column}' in session '{session_id}' to {new_type}.")

        # ✅ Force conversion explicitly
        try:
            if new_type == "int64":
                df[column] = df[column].astype("int64")
            elif new_type == "float64":
                df[column] = df[column].astype("float64")
            elif new_type == "object":  # Generic string conversion
                df[column] = df[column].astype("object")
            elif new_type == "boolean":
                df[column] = df[column].astype("boolean")
            elif new_type == "datetime64":
                df[column] = pd.to_datetime(df[column], errors="coerce")
            elif new_type == "timedelta64":
                df[column] = pd.to_timedelta(df[column], errors="coerce")
            elif new_type == "date":
                df[column] = pd.to_datetime(df[column], errors="coerce").dt.date
            elif new_type == "time":
                df[column] = pd.to_datetime(df[column], errors="coerce").dt.time
            elif new_type == "currency":
                df[column] = df[column].replace("[\$,]", "", regex=True).astype("float64")  # Remove `$` and convert
            elif new_type == "percentage":
                df[column] = df[column].replace("[%]", "", regex=True).astype("float64") / 100  # Convert `85%` → `0.85`
            elif new_type == "category":
                df[column] = df[column].astype("category")
            else:
                raise ValueError(f"Unsupported conversion type: {new_type}")

            # ✅ Overwrite the session explicitly
            add_session(session_id, df.copy(), session["name"])

            # ✅ Debug: Confirm session update
            session_after = get_session(session_id)
            logging.info(f"🔍 Session {session_id} after update:\n{session_after['df'].dtypes}")

            return jsonify({"message": f"Converted {column} to {new_type}"}), 200

        except Exception as e:
            logging.error(f"❌ Error converting {column} in session {session_id}: {e}")
            return jsonify({"error": str(e)}), 400

    except Exception as e:
        logging.error(f"❌ Unexpected error in convert_datatype: {e}")
        return jsonify({"error": str(e)}), 500











@data_routes.route("/replace_value/<session_id>", methods=["POST"])
def replace_value(session_id):
    """Replace a specific substring within a column in the dataset."""
    try:
        data = request.json
        column = data.get("column")
        find_value = data.get("find_value", "")
        replace_with = data.get("replace_with", "")

        session = get_session(session_id)
        if session is None:
            return jsonify({"error": "Session not found"}), 404

        df = session["df"].copy()  # Work with a COPY

        if column not in df.columns:
            return jsonify({"error": "Column not found"}), 400

        logging.info(f"🔄 Replacing '{find_value}' with '{replace_with}' in column '{column}' (Session: {session_id})")

        # ✅ Perform substring replacement for all values in the column
        df[column] = df[column].astype(str).str.replace(find_value, replace_with, regex=False)

        # ✅ Overwrite the session explicitly
        add_session(session_id, df.copy(), session["name"])

        return jsonify({
            "message": f"✅ Successfully replaced '{find_value}' with '{replace_with}' in column '{column}'",
            "updated_column": column
        }), 200

    except Exception as e:
        logging.error(f"❌ Error replacing value in session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500