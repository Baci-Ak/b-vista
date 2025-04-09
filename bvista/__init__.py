from .notebook_integration import show
from .server_manager import start_backend

try:
    # Dynamically read version from pyproject.toml
    from importlib.metadata import version
    __version__ = version("bvista")
except Exception:
    __version__ = "unknown"

try:
    start_backend()
except Exception as e:
    print(f"⚠️ Failed to start backend: {e}")

