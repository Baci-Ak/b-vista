import logging
import os
from backend.config import LOG_LEVEL  # ✅ Import LOG_LEVEL from config

# ✅ Ensure logs directory exists dynamically
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Get script directory
LOG_DIR = os.path.join(BASE_DIR, "..", "logs")  # Move logs outside utils/
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Configure logging
LOG_FILE = os.path.join(LOG_DIR, "backend.log")

logging.basicConfig(
    level=LOG_LEVEL,  # ✅ Read log level from config
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),  # ✅ Overwrite logs on restart
        logging.StreamHandler(),  # ✅ Print logs to console
    ],
)

logger = logging.getLogger(__name__)  # ✅ More dynamic logging

def log_info(message):
    """Log informational messages."""
    logger.info(message)

def log_warning(message):
    """Log warnings."""
    logger.warning(message)

def log_error(message):
    """Log errors."""
    logger.error(message, exc_info=True)
