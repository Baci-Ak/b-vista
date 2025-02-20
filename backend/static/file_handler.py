import os
import time
import magic  # ✅ Ensure you install this with `pip install python-magic`
from flask import request, jsonify

# ✅ Dynamic Upload Folder Path
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
ALLOWED_EXTENSIONS = {"csv", "xlsx", "json"}
MAX_FILE_SIZE_MB = 50  # ✅ Set maximum file size limit (50MB)

# ✅ Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Check if the uploaded file has a valid extension and is not missing an extension."""
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS

def is_safe_file(file_path):
    """Check MIME type to ensure the file is a valid dataset."""
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    allowed_mime_types = {"text/csv", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/json"}
    return file_type in allowed_mime_types

def save_uploaded_file():
    """Handle file upload and save it to the server."""
    if "file" not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    # ✅ Check File Size
    if request.content_length > MAX_FILE_SIZE_MB * 1024 * 1024:
        return jsonify({"error": f"File is too large. Max size: {MAX_FILE_SIZE_MB}MB"}), 400

    if file and allowed_file(file.filename):
        # ✅ Append timestamp to filename to prevent overwrites
        filename, ext = os.path.splitext(file.filename)
        safe_filename = f"{filename}_{int(time.time())}{ext}"
        file_path = os.path.join(UPLOAD_FOLDER, safe_filename)

        file.save(file_path)

        # ✅ Ensure uploaded file is a valid dataset
        if not is_safe_file(file_path):
            os.remove(file_path)  # Delete unsafe file
            return jsonify({"error": "Invalid file type"}), 400

        return jsonify({"message": "File uploaded successfully", "file_path": file_path}), 200
    
    return jsonify({"error": "Invalid file format"}), 400
