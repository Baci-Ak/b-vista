import requests
import pandas as pd
import os
import sys
from IPython.core.display import display, HTML

# Define Backend API URL
API_URL = "http://127.0.0.1:5050"

def show(df=None, name=None, session_id=None):
    """Display the UI inside Jupyter Notebook with dataset switching support."""

    if df is not None and not isinstance(df, pd.DataFrame):
        raise ValueError("Input must be a Pandas DataFrame.")

    if df is not None:
        # ✅ Automatically infer variable name if `name` is not provided
        if name is None:
            import inspect
            frame = inspect.currentframe().f_back
            name = [var_name for var_name, var_val in frame.f_locals.items() if var_val is df]
            name = name[0] if name else "Untitled_Dataset"  # Default to "Untitled_Dataset" if name detection fails

        # ✅ Ensure a clean dataset name (no `.csv`)
        filename = name  # ✅ Keep dataset name clean

        # ✅ Fix Upload Issue: Encode CSV Properly
        files = {"file": (filename, df.to_csv(index=False).encode('utf-8'), "text/csv")}
        response = requests.post(f"{API_URL}/api/upload", files=files, data={"session_id": name})

        if response.status_code != 200:
            try:
                error_message = response.json().get('error', 'Unknown error')
            except:
                error_message = response.text  # Handle case where response is not JSON
            raise ValueError(f"Failed to load data: {error_message}")

        session_id = response.json()["session_id"]

    elif session_id:
        # ✅ Validate if session exists
        response = requests.get(f"{API_URL}/api/session/{session_id}")
        if response.status_code != 200:
            raise ValueError(f"Invalid session_id: {session_id}")

    else:
        # ✅ Get latest session if no session_id is provided
        response = requests.get(f"{API_URL}/api/get_sessions")
        sessions = response.json().get("sessions", {})
        if sessions:
            session_id = list(sessions.keys())[-1]  # Get the latest session
        else:
            raise ValueError("No active sessions available. Please upload a dataset first.")

    # ✅ Define Web UI URL
    server_url = f"{API_URL}/?session_id={session_id}"

    # ✅ Display the UI inside Jupyter Notebook
    iframe_html = f"""
    <iframe src="{server_url}" width="100%" height="600px" style="border:none;"></iframe>
    <p style="margin-top:10px;">
        <a href="{server_url}" target="_blank" style="font-size:14px; text-decoration:none; color:#007bff;">
            🔗 Open in Web Browser
        </a>
    </p>
    """
    display(HTML(iframe_html))
