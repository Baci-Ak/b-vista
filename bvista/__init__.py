from .notebook_integration import show
from .server_manager import start_backend
import os
import sys

try:
    from importlib.metadata import version
except ImportError:
    from importlib_metadata import version

try:
    __version__ = version("bvista")
except Exception:
    __version__ = "unknown"

# Avoid double-launch or recursion (e.g., during backend boot)
if os.getenv("BVISTA_BOOTING") != "1" and not hasattr(sys, "_bvista_backend_launched"):
    try:
        sys._bvista_backend_launched = True  # One-time safeguard
        start_backend(silent=True)
    except Exception as e:
        raise RuntimeError(f"❌ B-Vista backend failed to start: {e}")
