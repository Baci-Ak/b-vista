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

# Only auto-start in interactive environments (not CI/builds)
if (
    os.getenv("BVISTA_BOOTING") != "1"
    and not hasattr(sys, "_bvista_backend_launched")
    and (hasattr(sys, 'ps1') or sys.stdin.isatty())  # ensures it's an interactive shell
):
    try:
        sys._bvista_backend_launched = True
        start_backend(silent=True)
    except Exception as e:
        raise RuntimeError(f"❌ B-Vista backend failed to start: {e}")

