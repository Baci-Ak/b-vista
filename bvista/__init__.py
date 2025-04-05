from .notebook_integration import show
from .server_manager import start_backend

# Automatically start the backend silently (no logs unless it fails)
start_backend(silent=True)
