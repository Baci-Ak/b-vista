import pandas as pd
import os

def load():
    """
    Load the Titanic dataset as a pandas DataFrame.

    Returns:
        pd.DataFrame: Titanic dataset
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "titanic.csv")
    return pd.read_csv(file_path)
