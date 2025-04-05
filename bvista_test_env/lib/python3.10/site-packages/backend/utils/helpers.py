# This file contains utility functions used across the backend to handle common tasks.
import os
import json
import pandas as pd
from datetime import datetime

def ensure_directory_exists(directory):
    """Ensure that a directory exists, create it if necessary."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_json(file_path, data):
    """Save a dictionary as a JSON file."""
    with open(file_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, indent=4)

def load_json(file_path):
    """Load a dictionary from a JSON file."""
    if not os.path.exists(file_path):
        return {}  # ✅ Return an empty dictionary instead of None
    with open(file_path, "r", encoding="utf-8") as json_file:
        return json.load(json_file)

def timestamp():
    """Generate a timestamp string for filenames and logs."""
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

def save_dataframe_to_csv(df, file_path):
    """Save a Pandas DataFrame to a CSV file."""
    df.to_csv(file_path, index=False)

def load_dataframe_from_csv(file_path):
    """Load a Pandas DataFrame from a CSV file with error handling."""
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path)
        except Exception as e:
            print(f"❌ Error loading CSV file {file_path}: {e}")
            return None
    return None
