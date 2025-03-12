# ✅ API Routes for Dataset Management
from flask import Blueprint, request, jsonify
import pandas as pd
import logging
import re
from datetime import datetime, timedelta
import json
from models.data_manager import add_session, get_session, delete_session, get_available_sessions
import os 
import pickle
from models.descriptive_stats import compute_descriptive_stats  # Import the function
from models.correlation import (
    compute_correlation_matrix,
    compute_spearman_correlation_matrix,
    compute_kendall_correlation_matrix,
    compute_partial_correlation_matrix,
    compute_distance_correlation_matrix,
    compute_mutual_information_matrix,
    compute_robust_correlation_matrix
)


from models.distribution_analysis import (generate_histogram,
                                          generate_box_plot
)



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

        # ✅ Try reading the Pickle file safely
        try:
            df = pickle.loads(file.read())  # ✅ Secure Pickle loading
            if not isinstance(df, pd.DataFrame):
                raise ValueError("Uploaded Pickle file does not contain a valid Pandas DataFrame.")
        except Exception as e:
            logging.error(f"❌ Invalid Pickle file: {file.filename} - {e}")
            return jsonify({"error": f"Invalid or corrupted Pickle file: {str(e)}"}), 400

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
    """Update a specific cell in the dataset and broadcast only the change via WebSocket."""
    try:
        data = request.json
        column = data.get("column")
        row_index = data.get("row_index")
        new_value = data.get("new_value")

        print(f"📝 Incoming cell update: Session {session_id} | Row {row_index}, Column {column} → {new_value}")

        # ✅ Retrieve the dataset session
        session = get_session(session_id)
        if session is None:
            return jsonify({"error": "Session not found"}), 404

        df = session["df"]

        # ✅ Ensure the column exists
        if column not in df.columns:
            return jsonify({"error": "Invalid column"}), 400

        # ✅ Ensure row index is within range
        if row_index < 0 or row_index >= len(df):
            return jsonify({"error": "Invalid row index"}), 400

        # ✅ Update only the specific cell
        df.at[row_index, column] = new_value

        # ✅ Broadcast only the changed value instead of the full DataFrame
        from websocket.socket_manager import socketio
        socketio.emit("update_cell", {
            "session_id": session_id,
            "row_index": row_index,
            "column": column,
            "new_value": new_value
        }, room=session_id)

        logging.info(f"🔄 Updated cell: [{row_index}, {column}] → '{new_value}'")

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




# ✅ Convert Number to HH:MM:SS
def format_hours(value):
    """Converts a number (seconds) into HH:MM:SS format like Excel."""
    if pd.notna(value) and isinstance(value, (int, float)):
        hours, remainder = divmod(int(value * 86400), 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return value  # Return as-is if NaN or not a number

# ✅ Convert HH:MM:SS to  fractional day number
def parse_hours(value):
    """Convert HH:MM:SS format back to decimal time fraction of a day."""
    if isinstance(value, str) and re.match(r"^\d{1,2}:\d{2}:\d{2}$", value):
        h, m, s = map(int, value.split(":"))
        return round((h * 3600 + m * 60 + s) / 86400, 10)  # Convert to fraction of a day
    return None if pd.isna(value) else value  # Preserve NaN values

# ✅ Convert Number to Currency
def format_currency(value, symbol="$"):
    """Formats a number into a currency string (e.g., $1,234.56)."""
    if pd.notna(value) and isinstance(value, (int, float)):
        return f"{symbol}{value:,.2f}"
    return value  # Return as-is if NaN or not a number

# ✅ Route: Convert Data Type
@data_routes.route("/convert_datatype/<session_id>", methods=["POST"])
def convert_datatype(session_id):
    """Convert the data type of a specified column and persist it in the session."""
    try:
        data = request.json
        column = data.get("column")
        new_type = data.get("new_type")
        currency_symbol = data.get("currency_symbol", "$")  # Default "$"

        session = get_session(session_id)
        if session is None:
            logging.error(f"❌ Session {session_id} not found.")
            return jsonify({"error": "Session not found"}), 404

        df = session["df"].copy()  # ✅ Work with a COPY

        if column not in df.columns:
            logging.error(f"❌ Column {column} not found in session {session_id}.")
            return jsonify({"error": "Column not found"}), 400

        logging.info(f"🔄 Converting column '{column}' in session '{session_id}' to {new_type}.")

        # ✅ Handle missing values: Ensure NaN stays None when converting numeric types
        if df[column].dtype in ["float64", "int64"]:
            df[column] = df[column].where(pd.notna(df[column]), None)


        # ✅ Handle missing values: Ensure NaN stays None when converting numeric types
        if df[column].dtype in ["float64", "int64"]:
            df[column] = df[column].where(pd.notna(df[column]), None)



        # ✅ Improved Object Column Handling:
        if df[column].dtype == "object":
            contains_only_numbers = df[column].dropna().astype(str).str.replace(".", "", 1).str.isnumeric().all()
            contains_words = df[column].dropna().astype(str).str.isalpha().any()
            contains_symbols = df[column].dropna().astype(str).str.contains(r"[^0-9.\s]", regex=True).any()

            # ✅ Allow numeric-like strings to be converted to numbers
            if contains_only_numbers:
                df[column] = pd.to_numeric(df[column], errors="coerce")

            # ❌ Prevent conversion if column has words or symbols
            elif contains_words or contains_symbols:
                return jsonify({"error": f"Cannot convert column '{column}' to {new_type} because it contains non-numeric values."}), 400






        # ✅ Perform Type Conversion
        try:
            if new_type == "int64":
                df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")

            elif new_type == "float64":
                df[column] = pd.to_numeric(df[column], errors="coerce").astype("float64")


            elif new_type == "boolean":
                df[column] = df[column].astype(str).str.lower().map(
                    {"true": True, "false": False, "yes": True, "no": False, "1": True, "0": False}
                ).astype("boolean")

            elif new_type == "datetime64":
                df[column] = pd.to_datetime(df[column], errors="coerce")

            elif new_type == "date":
                df[column] = pd.to_datetime(df[column], errors="coerce").dt.date  # Convert to date format
                df[column] = df[column].apply(lambda x: str(x) if pd.notna(x) else None)  # Replace NaT with None

            elif new_type == "hour":
                if df[column].dtype in ["float64", "int64"]:
                    df[column] = df[column].apply(lambda x: format_hours(x) if pd.notna(x) else None)
                elif pd.api.types.is_datetime64_any_dtype(df[column]):
                    df[column] = df[column].apply(lambda x: x.strftime("%H:%M:%S") if pd.notna(x) else None)
                elif pd.api.types.is_object_dtype(df[column]):
                    df[column] = df[column].apply(lambda x: parse_hours(x) if pd.notna(x) else None)
                else:
                    return jsonify({"error": "Hour conversion only works on numbers and time columns."}), 400

            elif new_type == "currency":
                if df[column].dtype in ["float64", "int64"]:
                    df[column] = df[column].apply(lambda x: format_currency(x, currency_symbol) if pd.notna(x) else None)
                else:
                    return jsonify({"error": "Currency conversion is only supported for numeric columns."}), 400

            elif new_type == "percentage":
                if df[column].dtype == "object" and df[column].str.endswith("%").all():
                    return jsonify({"error": "Cannot convert percentage strings to numeric directly. Remove '%' first."}), 400
                elif df[column].dtype in ["float64", "int64"]:
                    df[column] = df[column].apply(lambda x: f"{x * 100:.2f}%" if pd.notna(x) else None)
                else:
                    return jsonify({"error": "Percentage conversion is only supported for numeric columns."}), 400

            elif new_type == "category":
                df[column] = df[column].astype("category")

            elif new_type == "object":
                df[column] = df[column].astype(str).replace("nan", None)

            else:
                return jsonify({"error": f"Unsupported conversion type: {new_type}"}), 400

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
    """Replace a specific substring or handle missing values within a column in the dataset."""
    try:
        data = request.json
        column = data.get("column")
        find_value = data.get("find_value", "").strip()  # Ensure correct handling of spaces
        replace_with = data.get("replace_with", "").strip()  # Replacement value

        session = get_session(session_id)
        if session is None:
            return jsonify({"error": "Session not found"}), 404

        df = session["df"].copy()  # ✅ Work with a COPY

        if column not in df.columns:
            return jsonify({"error": "Column not found"}), 400

        logging.info(f"🔄 Replacing '{find_value}' with '{replace_with}' in column '{column}' (Session: {session_id})")

        # ✅ **Handling None Values Replacement**
        if find_value == "":
            df[column] = df[column].apply(lambda x: replace_with if pd.isna(x) else x)

        # ✅ **Perform Substring Replacement Without Affecting None Values**
        else:
            df[column] = df[column].apply(lambda x: str(x).replace(find_value, replace_with) if pd.notna(x) else x)

        # ✅ Overwrite the session explicitly
        add_session(session_id, df.copy(), session["name"])

        return jsonify({
            "message": f"✅ Successfully replaced '{find_value}' with '{replace_with}' in column '{column}'",
            "updated_column": column
        }), 200

    except Exception as e:
        logging.error(f"❌ Error replacing value in session {session_id}: {e}")
        return jsonify({"error": str(e)}), 500




# ✅ Route: Compute Descriptive Statistics

@data_routes.route("/descriptive_stats/<session_id>", methods=["GET"])
def get_descriptive_stats(session_id):
    """API Endpoint to retrieve descriptive statistics for a dataset session."""
    stats = compute_descriptive_stats(session_id)
    
    if "error" in stats:
        return jsonify(stats), 404  # Return 404 if session not found

    return jsonify(stats), 200  # Return statistics as JSON


# ✅ Route: Get column names for a selected dataset session
@data_routes.route("/get_columns/<session_id>", methods=["GET"])
def get_columns(session_id):
    """
    API Endpoint to retrieve column names for a selected dataset session.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 404

    df = session["df"]  # ✅ Retrieve the DataFrame
    columns = df.columns.tolist()  # ✅ Extract column names

    return jsonify({"columns": columns}), 200  # ✅ Return as JSON





@data_routes.route("/correlation_matrix", methods=["POST"])
def get_correlation_matrix():
    """
    API Endpoint to compute and return different types of correlation matrices.
    Expects a JSON payload with 'session_id', 'columns', and 'method'.
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        selected_columns = data.get("columns", None)
        method = data.get("method", "pearson")  # Default to Pearson

        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400

        # ✅ Select correlation method
        if method == "pearson":
            result = compute_correlation_matrix(session_id, selected_columns)
        elif method == "spearman":
            result = compute_spearman_correlation_matrix(session_id, selected_columns)
        elif method == "kendall":
            result = compute_kendall_correlation_matrix(session_id, selected_columns)
        elif method == "partial":
            result = compute_partial_correlation_matrix(session_id, selected_columns)
        elif method == "distance":
            result = compute_distance_correlation_matrix(session_id, selected_columns)
        elif method == "mutual_information":
            result = compute_mutual_information_matrix(session_id, selected_columns)
        elif method == "robust":  
            result = compute_robust_correlation_matrix(session_id, selected_columns)
        else:
            return jsonify({"error": "Invalid correlation method"}), 400

        if "error" in result:
            return jsonify(result), 400

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    








@data_routes.route("/distribution_analysis", methods=["POST"])
def get_distribution_analysis():
    """
    API Endpoint to generate distribution plots.
    Expects a JSON payload with 'session_id', 'columns', 'plot_type', and optional parameters.
    """
    try:
        data = request.json
        session_id = data.get("session_id")
        selected_columns = data.get("columns", [])
        plot_type = data.get("plot_type", "histogram")  # Default to histogram
        show_kde = data.get("show_kde", True)  # Default to True
        colors = data.get("colors", {})  # Allow user to pass colors dynamically

        if not session_id:
            return jsonify({"error": "Session ID is required"}), 400
        if not selected_columns:
            return jsonify({"error": "At least one column must be selected"}), 400

        # ✅ Call the appropriate function based on the plot type
        if plot_type == "histogram":
            return generate_histogram(session_id, selected_columns, show_kde, colors)
        elif plot_type == "boxplot":
            return generate_box_plot(session_id, selected_columns)
        else:
            return jsonify({"error": "Invalid plot type. Choose 'histogram' or 'boxplot'"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500




