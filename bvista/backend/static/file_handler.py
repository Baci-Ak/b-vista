import os
import time
import pickle
from flask import request, jsonify

# ✅ Dynamic Upload Folder Path
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"pkl"}  # ✅ Only allow Pickle files

# ✅ Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has a valid .pkl extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def is_valid_pickle(file_path):
    """Ensure the uploaded file is a valid Pickle file."""
    try:
        with open(file_path, "rb") as f:
            pickle.load(f)  # ✅ Try loading Pickle to confirm validity
        return True
    except Exception:
        return False  # ❌ Invalid Pickle file

def save_uploaded_file():
    """Handle file upload and save it securely."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = f"{int(time.time())}.pkl"  # ✅ Generate a unique filename
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # ✅ Validate Pickle file
        if not is_valid_pickle(file_path):
            os.remove(file_path)  # ❌ Delete invalid file
            return jsonify({"error": "Invalid or corrupted Pickle file"}), 400

        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200

    return jsonify({"error": "Invalid file format. Only .pkl files are allowed."}), 400
