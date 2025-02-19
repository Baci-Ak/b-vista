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
        # Load new DataFrame
        response = requests.post(f"{API_URL}/api/load_data", json={"data": df.to_dict(orient="records"), "name": name})
        if response.status_code != 200:
            raise ValueError(f"Failed to load data: {response.json().get('message', 'Unknown error')}")

        session_id = response.json()["session_id"]
        server_url = response.json()["url"]
    
    elif session_id:
        # Switch to existing session
        response = requests.get(f"{API_URL}/api/get_data/{session_id}")
        if response.status_code != 200:
            raise ValueError(f"Invalid session_id: {session_id}")
        server_url = API_URL
    
    else:
        # Get latest session
        response = requests.get(f"{API_URL}/api/get_sessions")
        sessions = response.json().get("sessions", {})
        if sessions:
            session_id = list(sessions.keys())[-1]  # Get the latest session
            server_url = API_URL
        else:
            raise ValueError("No active sessions available. Please load a dataset first.")

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
