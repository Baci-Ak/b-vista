from .notebook_integration import show
from .server_manager import start_backend

try:
    start_backend()
except Exception as e:
    print(f"⚠️ Failed to start backend: {e}")
