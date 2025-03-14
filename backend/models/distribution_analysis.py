import pandas as pd
import numpy as np
import seaborn as sns
from models.data_manager import get_session
from flask import jsonify
from scipy.stats import gaussian_kde, stats


def generate_histogram(session_id, selected_columns, show_kde=True, colors=None):
    """
    Generate histogram data for selected numeric columns.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :param show_kde: Boolean, whether to include KDE line.
    :return: JSON response with histogram data.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return {"error": f"Columns not found: {missing_cols}"}

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in numeric_cols]

    if not selected_numeric_columns:
        return {"error": "None of the selected columns are numeric"}

    histogram_data = {}

    for col in selected_numeric_columns:
        data = df[col].dropna()
        if data.empty:
            continue

        # Compute histogram bins and frequencies
        bins = np.histogram_bin_edges(data, bins="auto")  # Auto-binning based on data distribution
        hist, bin_edges = np.histogram(data, bins=bins)

        # Compute KDE (using SciPy)
        kde_x, kde_y = None, None
        if show_kde and len(data) > 1:
            kde_model = gaussian_kde(data, bw_method="scott")  # Scott's rule for bandwidth
            kde_x = np.linspace(data.min(), data.max(), 100).tolist()  # 100 smooth points
            kde_y = kde_model(np.array(kde_x)).tolist()  # KDE estimates

        # Compute statistics
        mean_value = float(data.mean())
        median_value = float(data.median())
        mode_value = float(data.mode().iloc[0]) if not data.mode().empty else None

        # Store results in dictionary
        histogram_data[col] = {
            "bins": bin_edges.tolist(),
            "frequencies": hist.tolist(),
            "kde_x": kde_x if kde_x else [],
            "kde_y": kde_y if kde_y else [],
            "mean": mean_value,
            "median": median_value,
            "mode": mode_value,
        }

    return jsonify({
        "session_id": session_id,
        "histograms": histogram_data
    })








def generate_box_plot(session_id, selected_columns):
    """
    Generate box plot data for selected numeric columns.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :return: JSON response with box plot data.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return {"error": f"Columns not found: {missing_cols}"}

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in numeric_cols]

    if not selected_numeric_columns:
        return {"error": "None of the selected columns are numeric"}

    box_plot_data = {}

    for col in selected_numeric_columns:
        data = df[col].dropna()
        if data.empty:
            continue

        # Compute quartiles and IQR
        q1 = np.percentile(data, 25)
        median = np.percentile(data, 50)
        q3 = np.percentile(data, 75)
        iqr = q3 - q1

        # Compute min and max (excluding outliers)
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        min_value = data[data >= lower_bound].min()
        max_value = data[data <= upper_bound].max()

        # Identify outliers
        outliers = data[(data < lower_bound) | (data > upper_bound)].tolist()

        # Store box plot data
        box_plot_data[col] = {
            "min": float(min_value),
            "q1": float(q1),
            "median": float(median),
            "q3": float(q3),
            "max": float(max_value),
            "outliers": outliers,
            #"raw_values": data.tolist()  # ✅ Send full column values
        }

    return jsonify({
        "session_id": session_id,
        "box_plots": box_plot_data
    })









def generate_qq_plot(session_id, selected_columns):
    """
    Generate QQ-Plot data for selected numeric columns and compute normality tests.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :return: JSON response with QQ-Plot data and statistical summaries.
    """
    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return {"error": f"Columns not found: {missing_cols}"}

    # Select only numeric columns
    numeric_cols = df.select_dtypes(include=["int64", "float64"]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in numeric_cols]

    if not selected_numeric_columns:
        return {"error": "None of the selected columns are numeric"}

    qq_plot_data = {}

    for col in selected_numeric_columns:
        data = df[col].dropna()
        if data.empty:
            continue

        # Generate theoretical quantiles (normal distribution)
        (theoretical_quantiles, sample_quantiles), (slope, intercept, r_value) = stats.probplot(data, dist="norm")

        # Compute normality statistics
        mean_value = float(data.mean())
        median_value = float(data.median())
        std_dev = float(data.std())

        # Normality tests
        normality_tests = {}

        if len(data) < 5000:
            # ✅ Shapiro-Wilk Test (Best for N ≤ 5000)
            shapiro_stat, shapiro_p = stats.shapiro(data)
            normality_tests["Shapiro-Wilk"] = {"statistic": float(shapiro_stat), "p_value": float(shapiro_p)}

        # ✅ Anderson-Darling Test (Works for all dataset sizes)
        anderson_result = stats.anderson(data, dist="norm")
        normality_tests["Anderson-Darling"] = {
            "statistic": float(anderson_result.statistic),
            "critical_values": anderson_result.critical_values.tolist(),
            "significance_levels": anderson_result.significance_level.tolist(),
        }

        if len(data) >= 5000:
            # ✅ Kolmogorov-Smirnov Test (For large datasets)
            ks_stat, ks_p = stats.kstest(data, "norm", args=(mean_value, std_dev))
            normality_tests["Kolmogorov-Smirnov"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}

            # ✅ D’Agostino & Pearson Test (For large datasets)
            dagostino_stat, dagostino_p = stats.normaltest(data)
            normality_tests["D’Agostino-Pearson"] = {"statistic": float(dagostino_stat), "p_value": float(dagostino_p)}

        qq_plot_data[col] = {
            "theoretical_quantiles": theoretical_quantiles.tolist(),
            "sample_quantiles": sample_quantiles.tolist(),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_value**2),  # Goodness of fit
            "mean": mean_value,
            "median": median_value,
            "std_dev": std_dev,
            "normality_tests": normality_tests  # ✅ Includes multiple normality tests
        }

    return jsonify({
        "session_id": session_id,
        "qq_plots": qq_plot_data
    })

