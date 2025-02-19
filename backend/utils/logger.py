import logging
import os

# ✅ Ensure logs directory exists
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

# ✅ Configure logging
LOG_FILE = os.path.join(LOG_DIR, "backend.log")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8"),
        logging.StreamHandler(),  # ✅ Also log to console
    ],
)

logger = logging.getLogger("B-Vista")

def log_info(message):
    """Log informational messages."""
    logger.info(message)

def log_warning(message):
    """Log warnings."""
    logger.warning(message)

def log_error(message):
    """Log errors."""
    logger.error(message, exc_info=True)
