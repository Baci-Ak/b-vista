import pandas as pd
import numpy as np
from scipy.stats import shapiro, zscore
from models.data_manager import get_session

def compute_descriptive_stats(session_id):
    """
    Compute descriptive statistics for all column types (numeric, categorical, boolean, datetime).
    
    :param session_id: The session ID of the dataset.
    :return: A dictionary containing descriptive statistics.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()  # ✅ Work with a copy to avoid modifying original data

    # ✅ Ensure DataFrame is not empty
    if df.empty:
        return {"error": "Dataset is empty"}

    # ✅ Compute descriptive statistics for all columns
    stats = df.describe()

    # ✅ Compute additional statistics
    missing_values = df.isnull().sum()  # Missing values per column
    variance = df.var(numeric_only=True)  # Variance (Only for numeric)
    skewness = df.skew(numeric_only=True)  # Skewness (Only for numeric)
    kurtosis = df.kurtosis(numeric_only=True)  # Kurtosis (Only for numeric)

    # ✅ Compute mode for all columns (Returns multiple values, so we take the first mode)
    mode_values = df.mode().iloc[0] if not df.mode().empty else pd.Series([None] * len(df.columns), index=df.columns)

    # ✅ Compute Shapiro-Wilk Test (Normality Test) for numeric columns
    shapiro_wilk_results = df.select_dtypes(include=[np.number]).apply(
        lambda x: shapiro(x.dropna()) if len(x.dropna()) > 3 else (None, None)
    )

    # ✅ Extract W-statistic and p-value separately
    shapiro_wilk_w = shapiro_wilk_results.apply(lambda x: x[0])  # W-statistic
    shapiro_wilk_p = shapiro_wilk_results.apply(lambda x: x[1])  # p-value

                                     
    # ✅ Compute Z-score for numeric columns
    z_scores = df.select_dtypes(include=[np.number]).apply(zscore)
                                                                               
    # ✅ Convert additional statistics to DataFrame                          
    additional_stats = pd.DataFrame({
        "missing values": missing_values,
        "variance": variance,                          
        "skewness": skewness,                      
        "kurtosis": kurtosis,
        "mode": mode_values,
        "shapiro-wilk W-statistic": shapiro_wilk_w,
        "shapiro-wilk p-value": shapiro_wilk_p
    }).T  # Transpose to match existing stats structure
                                    
    # ✅ Concatenate with existing stats
    stats = pd.concat([stats, additional_stats])

    # ✅ Explicitly replace all NaN, NaT, and Inf values with None
    stats = stats.replace([np.nan, np.inf, -np.inf, pd.NaT], None)

    # ✅ Convert DataFrame to JSON-safe dictionary
    stats_dict = stats.to_dict()

    return {
        "session_id": session_id,
        "statistics": stats_dict
    }
