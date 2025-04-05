import pandas as pd
import numpy as np
from models.data_manager import get_session
from sklearn.linear_model import LinearRegression
import dcor
import pymc as pm  # Instead of pymc3
from scipy.spatial.distance import pdist, squareform
from sklearn.feature_selection import mutual_info_regression
import pingouin as pg  # ✅ Import Pingouin for robust correlation
from scipy.stats.mstats import winsorize


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


# Kendall Tau

def compute_kendall_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the Kendall Tau correlation matrix for a given dataset session.

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

    # ✅ Select numeric columns BEFORE forcing conversion
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

    # ✅ Compute Kendall Tau correlation matrix, filling NaN with 0
    correlation_matrix = df.corr(method="kendall").fillna(0)

    # ✅ Convert to a JSON-friendly dictionary
    correlation_dict = correlation_matrix.round(2).to_dict()

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": correlation_dict
    }





# Partial Correlation

def compute_partial_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the partial correlation matrix for a given dataset session.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of column names to compute correlation on.
    :return: A dictionary containing the partial correlation matrix.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ Select numeric columns only
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if not numeric_cols:
        return {"error": "No numeric columns found for correlation computation"}

    # ✅ Filter only numeric columns from selected ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols  # Default to all numeric columns

    # ✅ Drop rows where all selected values are NaN
    df = df[selected_columns].dropna(how="all")

    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for correlation"}

    # ✅ Handle constant columns (which would cause division errors)
    constant_cols = [col for col in df.columns if df[col].nunique() == 1]
    if constant_cols:
        return {"error": f"Cannot compute partial correlation. These columns have constant values: {constant_cols}"}    

    # ✅ Compute Partial Correlation
    n = df.shape[1]
    partial_corr_matrix = np.eye(n)  # Identity matrix (diagonal = 1)

    for i in range(n):
        for j in range(i + 1, n):  # Upper triangle iteration
            X = df.drop(columns=[selected_columns[i], selected_columns[j]])
            y1, y2 = df[selected_columns[i]], df[selected_columns[j]]

            try:
                if X.shape[1] == 0:  # If no control variables, use Pearson correlation
                    corr = np.corrcoef(y1, y2)[0, 1]
                else:
                    # Regress y1 and y2 separately on the control variables
                    reg_y1 = LinearRegression().fit(X, y1)
                    reg_y2 = LinearRegression().fit(X, y2)

                    # Compute residuals
                    residual_y1 = y1 - reg_y1.predict(X)
                    residual_y2 = y2 - reg_y2.predict(X)

                    # Compute correlation between residuals
                    corr = np.corrcoef(residual_y1, residual_y2)[0, 1]

                # ✅ Handle undefined values (e.g., NaN due to multicollinearity)
                if np.isnan(corr) or np.isinf(corr):
                    corr = 0.0  # Replace NaN or Inf with 0

                # ✅ Fill the symmetric matrix
                partial_corr_matrix[i, j] = partial_corr_matrix[j, i] = round(corr, 2)

            except Exception:
                partial_corr_matrix[i, j] = partial_corr_matrix[j, i] = 0.0  # Default to 0 in case of errors

    # ✅ Convert to dictionary for JSON response
    partial_correlation_dict = {
        selected_columns[i]: {selected_columns[j]: partial_corr_matrix[i, j] for j in range(n)}
        for i in range(n)
    }

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": partial_correlation_dict
    }





def compute_distance_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the Distance Correlation matrix for a given dataset session.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of column names to compute correlation on.
    :return: A dictionary containing the distance correlation matrix.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ Select numeric columns only
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if not numeric_cols:
        return {"error": "No numeric columns found for correlation computation"}

    # ✅ Filter only numeric columns from selected ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols  # Default to all numeric columns

    # ✅ Drop rows where all selected values are NaN
    df = df[selected_columns].dropna(how="all")

    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for correlation"}

    # ✅ Compute Distance Correlation Matrix
    n = len(selected_columns)
    distance_corr_matrix = np.zeros((n, n), dtype=float)  # Initialize zero matrix

    for i in range(n):
        for j in range(i, n):  # Compute upper triangle only
            x, y = df[selected_columns[i]].values, df[selected_columns[j]].values

            # ✅ Drop NaN values consistently to keep array lengths the same
            valid_mask = ~np.isnan(x) & ~np.isnan(y)
            x_clean, y_clean = x[valid_mask], y[valid_mask]

            # ✅ Compute distance correlation only if data remains
            if len(x_clean) > 1 and len(y_clean) > 1:
                corr = dcor.distance_correlation(x_clean, y_clean)
            else:
                corr = 0.0  # Assign 0 if no valid data remains

            # ✅ Fill symmetric matrix and round values
            distance_corr_matrix[i, j] = distance_corr_matrix[j, i] = round(corr, 2)

    # ✅ Convert to JSON-friendly dictionary
    distance_correlation_dict = {
        selected_columns[i]: {selected_columns[j]: distance_corr_matrix[i, j] for j in range(n)}
        for i in range(n)
    }

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": distance_correlation_dict
    }






def compute_mutual_information_matrix(session_id, selected_columns=None):
    """
    Compute the Mutual Information (MI) matrix for a given dataset session.

    :param session_id: The session ID of the dataset.
    :param selected_columns: Optional list of column names to compute MI on.
    :return: A dictionary containing the MI matrix.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ Select numeric columns only
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()

    if not numeric_cols:
        return {"error": "No numeric columns found for MI computation"}

    # ✅ Filter only numeric columns from selected ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols  # Default to all numeric columns

    # ✅ Drop rows where all selected values are NaN
    df = df[selected_columns].dropna(how="all")

    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for MI computation"}

    # ✅ Compute Mutual Information Matrix
    n = len(selected_columns)
    mi_matrix = np.zeros((n, n), dtype=float)  # Initialize zero matrix

    for i in range(n):
        for j in range(i, n):  # Compute upper triangle only
            x, y = df[selected_columns[i]].values, df[selected_columns[j]].values

            # ✅ Drop NaN values consistently
            valid_mask = ~np.isnan(x) & ~np.isnan(y)
            x_clean, y_clean = x[valid_mask].reshape(-1, 1), y[valid_mask]

            # ✅ Ensure enough data points
            if len(x_clean) > 2 and len(y_clean) > 2:
                # Dynamically adjust n_neighbors
                n_neighbors = min(3, len(x_clean) - 1)
                mi = mutual_info_regression(x_clean, y_clean, discrete_features=False, n_neighbors=n_neighbors)[0]

                # ✅ Normalize MI between 0-1
                mi = max(mi, 0.01) / np.log(len(x_clean))
            else:
                mi = 0.01  # Assign small value instead of 0

            # ✅ Fill symmetric matrix and round values
            mi_matrix[i, j] = mi_matrix[j, i] = round(mi, 2)

    # ✅ Convert to JSON-friendly dictionary
    mi_correlation_dict = {
        selected_columns[i]: {selected_columns[j]: mi_matrix[i, j] for j in range(n)}
        for i in range(n)
    }

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": mi_correlation_dict
    }












def compute_robust_correlation_matrix(session_id, selected_columns=None):
    """
    Compute the Robust Correlation matrix using Winsorized data and Spearman correlation.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # ✅ Ensure dataset is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ Select numeric columns only
    numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
    if not numeric_cols:
        return {"error": "No numeric columns found for correlation computation"}

    # ✅ Filter only numeric columns from selected ones
    if selected_columns:
        selected_columns = [col for col in selected_columns if col in numeric_cols]
        if not selected_columns:
            return {"error": "None of the selected columns are numeric"}
    else:
        selected_columns = numeric_cols

    # ✅ Drop rows with NaNs in selected columns
    df = df[selected_columns].dropna(how="all")
    if df.shape[1] < 2:
        return {"error": "Not enough numeric columns for correlation"}

    n = len(selected_columns)
    robust_corr_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i, n):
            x, y = df[selected_columns[i]].values, df[selected_columns[j]].values

            # ✅ Winsorization to remove extreme outliers
            x_wins = winsorize(x, limits=[0.05, 0.05])
            y_wins = winsorize(y, limits=[0.05, 0.05])

            # ✅ Compute correlation using Spearman (robust alternative)
            corr = pg.corr(x_wins, y_wins, method="spearman").iloc[0, 1]

            robust_corr_matrix[i, j] = robust_corr_matrix[j, i] = round(corr, 2)

    # ✅ Convert to JSON-friendly dictionary
    robust_correlation_dict = {
        selected_columns[i]: {selected_columns[j]: robust_corr_matrix[i, j] for j in range(n)}
        for i in range(n)
    }

    return {
        "session_id": session_id,
        "selected_columns": selected_columns,
        "correlation_matrix": robust_correlation_dict
    }
