import os

# ✅ Flask App Configuration
FLASK_CONFIG = {
    "DEBUG": os.getenv("DEBUG", "False").lower() == "true",  # ✅ Dynamically set debug mode
    "HOST": "0.0.0.0",
    "PORT": int(os.getenv("PORT", 5050)),  # ✅ Ensure it matches backend/app.py
    "SECRET_KEY": os.getenv("SECRET_KEY", "supersecretkey"),
    "CORS_ALLOWED_ORIGINS": "*",
}

# ✅ WebSocket Configuration
SOCKET_CONFIG = {
    "CORS_ALLOWED_ORIGINS": "*",
    "ASYNC_MODE": "threading",  # ✅ Use "threading" for better stability
}

# ✅ Data Storage Configuration
DATA_CONFIG = {
    "TEMP_STORAGE_DIR": os.getenv("TEMP_STORAGE_DIR", "./temp_data"),
    "MAX_SESSION_AGE": 3600,  # Session expiration in seconds
}

# ✅ Ensure the TEMP_STORAGE_DIR exists
if not os.path.exists(DATA_CONFIG["TEMP_STORAGE_DIR"]):
    os.makedirs(DATA_CONFIG["TEMP_STORAGE_DIR"])
