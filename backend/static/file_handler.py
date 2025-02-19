# handles file uploads and downloads, allowing users to upload datasets for processing
import os
from flask import request, jsonify

UPLOAD_FOLDER = "backend/static/uploads"
ALLOWED_EXTENSIONS = {"csv", "xlsx", "json"}

# ✅ Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file():
    """Handle file upload and save it to the server."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(file_path)
        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200
    
    return jsonify({"error": "Invalid file format"}), 400
