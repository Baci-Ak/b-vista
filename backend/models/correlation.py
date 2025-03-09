import pandas as pd
from models.data_manager import get_session

def compute_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the correlation matrix for a given dataset session.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of column names to compute correlation on.
    :return: A dictionary containing the correlation matrix.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()  # ✅ Work with a COPY of the DataFrame

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ First, select numeric columns BEFORE forcing conversion
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if not numeric_cols:
        return {"error": "No numeric columns found for correlation computation"}

    # ✅ Filter selected columns to only include numeric ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols  # Default to all numeric columns

    # ✅ Drop rows where all values are NaN in selected columns
    df = df[selected_columns].dropna(how="all")

    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for correlation"}

    # ✅ Compute correlation matrix, filling NaN with 0
    correlation_matrix = df.corr().fillna(0)

    # ✅ Convert to a JSON-friendly dictionary
    correlation_dict = correlation_matrix.round(2).to_dict()

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": correlation_dict
    }


# Spearman Correlation


def compute_spearman_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the Spearman correlation matrix for a given dataset session.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of column names to compute correlation on.
    :return: A dictionary containing the Spearman correlation matrix.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()  # ✅ Work with a COPY of the DataFrame

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ First, select numeric columns BEFORE forcing conversion
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if not numeric_cols:
        return {"error": "No numeric columns found for correlation computation"}

    # ✅ Filter selected columns to only include numeric ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols  # Default to all numeric columns

    # ✅ Drop rows where all values are NaN in selected columns
    df = df[selected_columns].dropna(how="all")

    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for correlation"}

    # ✅ Compute Spearman correlation matrix, filling NaN with 0
    spearman_matrix = df.corr(method="spearman").fillna(0)

    # ✅ Convert to a JSON-friendly dictionary
    spearman_dict = spearman_matrix.round(2).to_dict()

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": spearman_dict
    }
