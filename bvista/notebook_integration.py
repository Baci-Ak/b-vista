import os
import sys
import re
import pickle
import requests
import pandas as pd
import inspect
import webbrowser

from IPython import get_ipython
from IPython.display import display, HTML

API_URL = "http://127.0.0.1:5050"


def is_backend_running(timeout=2):
    """Check if the backend server is running."""
    try:
        response = requests.get(f"{API_URL}/healthcheck", timeout=timeout)
        return response.status_code == 200
    except requests.RequestException:
        return False


def _in_notebook():
    """Detect if running in Jupyter notebook, Colab, or IPython shell."""
    try:
        shell = get_ipython().__class__.__name__
        return shell in ("ZMQInteractiveShell", "Shell")  # Covers Jupyter + IPython
    except Exception:
        return False


def _safe_name_from_variable(df):
    """Try to extract the name of the DataFrame variable from the caller's frame."""
    try:
        frame = inspect.currentframe().f_back
        for var_name, val in frame.f_locals.items():
            if val is df:
                return re.sub(r'[^a-zA-Z0-9_-]', '_', var_name)
    except Exception:
        pass
    return "Untitled_Dataset"


def show(df=None, name=None, session_id=None, open_browser=True, silent=False):
    """
    Launch the B-Vista interface in a notebook or browser.

    Args:
        df (pd.DataFrame): DataFrame to visualize.
        name (str): Optional custom name for session.
        session_id (str): Reconnect to previous session.
        open_browser (bool): If True, open web UI in browser (non-notebook use).
        silent (bool): Suppress print/log output.
    """
    # Ensure backend is alive
    if not is_backend_running():
        raise RuntimeError("❌ B-Vista backend is not running. Please start it before calling `bv.show()`.")

    if df is not None:
        if not isinstance(df, pd.DataFrame):
            raise ValueError("❌ The `df` argument must be a pandas DataFrame.")

        # Use fallback name if variable name not found
        name = name or _safe_name_from_variable(df)
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

        # Convert to pickle and upload
        try:
            df_bytes = pickle.dumps(df)
            files = {"file": (f"{name}.pkl", df_bytes, "application/octet-stream")}
            response = requests.post(f"{API_URL}/api/upload", files=files, data={"session_id": name, "name": name})
        except Exception as e:
            raise RuntimeError(f"❌ Failed to connect to backend: {e}")

        if response.status_code != 200:
            try:
                error_msg = response.json().get("error", "Unknown error")
            except Exception:
                error_msg = response.text
            raise RuntimeError(f"❌ Failed to upload dataset: {error_msg}")

        session_id = response.json().get("session_id")

    elif session_id:
        # Validate session ID
        check = requests.get(f"{API_URL}/api/session/{session_id}")
        if check.status_code != 200:
            raise ValueError(f"❌ Session ID not found: {session_id}")

    else:
        # Get latest available session
        response = requests.get(f"{API_URL}/api/get_sessions")
        sessions = response.json().get("sessions", {})
        if not sessions:
            raise RuntimeError("❌ No active session available. Please upload a dataset.")
        session_id = list(sessions.keys())[-1]

    session_url = f"{API_URL}/?session_id={session_id}"

    # Render in notebook or browser
    if _in_notebook():
        iframe_html = f"""
        <iframe src="{session_url}" width="100%" height="600px" style="border:none;"></iframe>
        <p style="margin-top:10px;">
            <a href="{session_url}" target="_blank" style="font-size:14px; text-decoration:none; color:#007bff;">
                🔗 Open in Web Browser
            </a>
        </p>
        """
        display(HTML(iframe_html))

    else:
        if not silent:
            print(f"🔗 B-Vista running at: {session_url}")
        if open_browser:
            try:
                webbrowser.open(session_url)
            except Exception:
                if not silent:
                    print("⚠️ Could not open browser. Please open manually:")
                    print(session_url)
