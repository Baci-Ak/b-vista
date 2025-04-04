import pandas as pd
import os

def load():
    """
    Load the testing dataset as a pandas DataFrame.

    Returns:
        pd.DataFrame: testing dataset
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "testing_data.csv")
    return pd.read_csv(file_path)
