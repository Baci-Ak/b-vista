# ✅ Configuration file for B-Vista Backend
import os
from dotenv import load_dotenv

# ✅ Load environment variables from a .env file
load_dotenv()

# ✅ General Configuration
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")

# ✅ Flask App Configuration
FLASK_HOST = os.getenv("FLASK_HOST", "127.0.0.1")  # Default to localhost
FLASK_PORT = int(os.getenv("FLASK_PORT", 5050))  # Ensure backend runs on correct port

# ✅ Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "bvista_db")
DB_USER = os.getenv("DB_USER", "bvista_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# ✅ WebSocket Configuration
SOCKET_PORT = int(os.getenv("SOCKET_PORT", 5001))

# ✅ Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
