from .notebook_integration import show
from .server_manager import start_backend

try:
    from importlib.metadata import version
except ImportError:
    # For Python < 3.8 fallback (if needed, but >=3.7 supported by pyproject.toml)
    from importlib_metadata import version

try:
    __version__ = version("bvista")
except Exception:
    __version__ = "unknown"

try:
    start_backend()
except Exception as e:
    print(f"⚠️ Failed to start backend: {e}")
