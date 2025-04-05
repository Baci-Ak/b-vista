import pandas as pd
import os

def load():
    """
    Load the Ames Housing dataset as a pandas DataFrame.

    Returns:
        pd.DataFrame: Ames Housing dataset
    """
    current_dir = os.path.dirname(__file__)
    file_path = os.path.join(current_dir, "ames_housing.csv")
    return pd.read_csv(file_path)
