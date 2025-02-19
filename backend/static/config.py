# This file centralizes configuration settings for the backend.
import os

# ✅ Flask App Configuration
FLASK_CONFIG = {
    "DEBUG": True,
    "HOST": "0.0.0.0",
    "PORT": int(os.getenv("PORT", 5000)),
    "SECRET_KEY": os.getenv("SECRET_KEY", "supersecretkey"),
    "CORS_ALLOWED_ORIGINS": "*",
}

# ✅ WebSocket Configuration
SOCKET_CONFIG = {
    "CORS_ALLOWED_ORIGINS": "*",
    "ASYNC_MODE": None,  # Can be set to 'eventlet' or 'gevent' if needed
}

# ✅ Data Storage Configuration
DATA_CONFIG = {
    "TEMP_STORAGE_DIR": os.getenv("TEMP_STORAGE_DIR", "./temp_data"),
    "MAX_SESSION_AGE": 3600,  # Session expiration in seconds
}
