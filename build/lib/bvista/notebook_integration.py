import requests
import pandas as pd
import os
import sys
from IPython.core.display import display, HTML
import pickle
import re

# Define Backend API URL
API_URL = "http://127.0.0.1:5050"

def is_backend_running():
    """Check if the backend server is running before making requests."""
    try:
        response = requests.get(f"{API_URL}/healthcheck", timeout=3)
        return response.status_code == 200
    except requests.RequestException:
        return False

def show(df=None, name=None, session_id=None):
    """Display the UI inside Jupyter Notebook with dataset switching support."""

    # ✅ Check if the backend is running before proceeding
    if not is_backend_running():
        raise ConnectionError("❌ B-Vista backend is not running. Please start the backend before using `bv.show(df)`. 🚀")

    if df is not None and not isinstance(df, pd.DataFrame):
        raise ValueError("❌ Input must be a Pandas DataFrame.")

    if df is not None:
        # Automatically infer variable name if `name` is not provided
        if name is None:
            import inspect
            frame = inspect.currentframe().f_back
            name = [var_name for var_name, var_val in frame.f_locals.items() if var_val is df]
            name = name[0] if name else "Untitled_Dataset"  # Default to "Untitled_Dataset" if name detection fails

        # Ensure dataset name is safe (no special characters)
        
        name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

        # Convert DataFrame to Pickle Binary Format
        df_bytes = pickle.dumps(df)  # Convert DataFrame to a binary object

        # Send Pickle file with correct filename
        files = {"file": (f"{name}.pkl", df_bytes, "application/octet-stream")}
        response = requests.post(f"{API_URL}/api/upload", files=files, data={"session_id": name, "name": name})

        if response.status_code != 200:
            try:
                error_message = response.json().get('error', 'Unknown error')
            except:
                error_message = response.text  # Handle case where response is not JSON
            raise ValueError(f"❌ Failed to upload dataset: {error_message}")

        session_id = response.json()["session_id"]
        #print(f"✅ Dataset '{name}' uploaded successfully. Session ID: {session_id}")

    elif session_id:
        # Validate if session exists
        response = requests.get(f"{API_URL}/api/session/{session_id}")
        if response.status_code != 200:
            raise ValueError(f"❌ Invalid session_id: {session_id}")

    else:
        # Get latest session if no session_id is provided
        response = requests.get(f"{API_URL}/api/get_sessions")
        sessions = response.json().get("sessions", {})
        if sessions:
            session_id = list(sessions.keys())[-1]  # Get the latest session
        else:
            raise ValueError("❌ No active sessions available. Please upload a dataset first.")

    # Define Web UI URL
    server_url = f"{API_URL}/?session_id={session_id}"

    # Display the UI inside Jupyter Notebook
    iframe_html = f"""
    <iframe src="{server_url}" width="100%" height="600px" style="border:none;"></iframe>
    <p style="margin-top:10px;">
        <a href="{server_url}" target="_blank" style="font-size:14px; text-decoration:none; color:#007bff;">
            🔗 Open in Web Browser
        </a>
    </p>
    """
    display(HTML(iframe_html))
