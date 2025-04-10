import pandas as pd
import numpy as np
import seaborn as sns
from bvista.backend.models.data_manager import get_session
from flask import jsonify
from scipy.stats import gaussian_kde, stats
from scipy import stats
















def generate_histogram(session_id, selected_columns, show_kde=True, colors=None):
    """
    Generate histogram data for selected numeric columns with optimized performance for large datasets.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :param show_kde: Boolean, whether to include KDE line.
    :return: JSON response with histogram data.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 400

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable"}), 400

    # ✅ Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return jsonify({"error": f"Columns not found: {missing_cols}"}), 400

    # ✅ Ensure only valid numeric columns are processed
    valid_numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in valid_numeric_cols]

    if not selected_numeric_columns:
        return jsonify({"error": "None of the selected columns are numeric. Please choose numeric columns only."}), 400

    histogram_data = {}

    for col in selected_numeric_columns:
        data = df[col].dropna()
        if data.empty:
            continue

        # ✅ Handle case where all values are the same (Single-value column)
        if data.nunique() == 1:
            unique_value = data.iloc[0]
            histogram_data[col] = {
                "bins": [unique_value - 0.5, unique_value + 0.5],
                "frequencies": [len(data)],
                "kde_x": [],
                "kde_y": [],
                "mean": float(unique_value),
                "median": float(unique_value),
                "mode": float(unique_value),
            }
            continue  # Skip further calculations for single-value columns

        # ✅ Smart bin selection: Compute only ONCE
        auto_bins = np.histogram_bin_edges(data, bins="auto")
        bin_count = min(50, max(5, len(auto_bins) - 1))  # Keep it reasonable
        bins = np.histogram_bin_edges(data, bins=bin_count)  # Final bin edges
        hist, bin_edges = np.histogram(data, bins=bins)

        # ✅ Compute KDE (Kernel Density Estimation) if needed
        kde_x, kde_y = None, None
        if show_kde and len(data) > 1:
            # ✅ Dynamically choose best bandwidth method
            bw_method = "scott" if len(data) <= 10000 else "silverman"

            # ✅ Downsample for large datasets (>50K rows) to speed up KDE
            sampled_data = data if len(data) <= 50000 else np.random.choice(data, 50000, replace=False)

            kde_model = gaussian_kde(sampled_data, bw_method=bw_method)
            kde_x = np.linspace(data.min(), data.max(), 1000).tolist()  # 1000 smooth points
            kde_y = kde_model(np.array(kde_x)).tolist()  # KDE estimates

        # ✅ Compute key statistics
        mean_value = float(data.mean())
        median_value = float(data.median())
        mode_value = float(data.mode().iloc[0]) if not data.mode().empty else None

        # ✅ Store results in dictionary
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
    }), 200




















def generate_box_plot(session_id, selected_columns):
    """
    Generate box plot data for selected numeric columns with optimized performance and edge case handling.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :return: JSON response with box plot data.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 400

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable"}), 400

    # ✅ Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return jsonify({"error": f"Columns not found: {missing_cols}"}), 400

    # ✅ Select only numeric columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in numeric_cols]

    if not selected_numeric_columns:
        return jsonify({"error": "None of the selected columns are numeric"}), 400

    # ✅ Drop NaN values from all selected columns at once
    valid_data = df[selected_numeric_columns].dropna()

    if valid_data.empty:
        return jsonify({"error": "No valid data available after removing NaNs"}), 400

    # ✅ Compute skewness for all columns at once
    skewness_values = valid_data.apply(lambda col: stats.skew(col, nan_policy="omit") if col.nunique() > 1 else np.nan)

    # ✅ Identify columns needing log transformation (Only for positive values)
    log_transform_flags = (skewness_values > 2) & valid_data.gt(0).all()

    # ✅ Apply log transformation where necessary
    transformed_data = valid_data.copy()
    transformed_data.loc[:, log_transform_flags] = np.log1p(transformed_data.loc[:, log_transform_flags])

    # ✅ Compute box plot statistics (vectorized)
    q1 = transformed_data.quantile(0.25)
    median = transformed_data.quantile(0.50)
    q3 = transformed_data.quantile(0.75)
    iqr = q3 - q1

    # ✅ Compute bounds for min/max
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    min_values = transformed_data.mask(transformed_data < lower_bound).min()
    max_values = transformed_data.mask(transformed_data > upper_bound).max()

    # ✅ Ensure min/max are valid (Handle zero-IQR cases)
    min_values.fillna(q1, inplace=True)
    max_values.fillna(q3, inplace=True)

    # ✅ Identify outliers efficiently
    outliers = {
        col: transformed_data[col][(transformed_data[col] < lower_bound[col]) | (transformed_data[col] > upper_bound[col])].tolist()
        for col in selected_numeric_columns
    }

    # ✅ Store results
    box_plot_data = {
        col: {
            "min": float(min_values[col]),
            "q1": float(q1[col]),
            "median": float(median[col]),
            "q3": float(q3[col]),
            "max": float(max_values[col]),
            "outliers": outliers[col] if outliers[col] else [],
            "log_transformed": bool(log_transform_flags[col]),  # ✅ Mark column if log-transformed
            "skewness": float(skewness_values[col]) if not np.isnan(skewness_values[col]) else "N/A"
        }
        for col in selected_numeric_columns
    }

    return jsonify({
        "session_id": session_id,
        "box_plots": box_plot_data
    }), 200










def generate_qq_plot(session_id, selected_columns):
    """
    Generate QQ-Plot data for selected numeric columns and compute normality tests,
    including 95% confidence bands for the regression fit.

    :param session_id: The session ID of the dataset.
    :param selected_columns: List of column names to include.
    :return: JSON response with QQ-Plot data and statistical summaries.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"}), 400

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable"}), 400

    # ✅ Ensure selected columns exist
    missing_cols = [col for col in selected_columns if col not in df.columns]
    if missing_cols:
        return jsonify({"error": f"Columns not found: {missing_cols}"}), 400

    # ✅ Select only numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    selected_numeric_columns = [col for col in selected_columns if col in numeric_cols]

    if not selected_numeric_columns:
        return jsonify({"error": "None of the selected columns are numeric"}), 400

    qq_plot_data = {}

    for col in selected_numeric_columns:
        data = df[col].dropna()
        
        # ✅ Ensure we have at least two valid numeric values
        data = data[np.isfinite(data)]
        if data.empty or len(data) < 2:
            continue

        # ✅ Handle case where all values are the same
        if data.nunique() == 1:
            unique_value = float(data.iloc[0])
            qq_plot_data[col] = {
                "theoretical_quantiles": [unique_value, unique_value],
                "sample_quantiles": [unique_value, unique_value],
                "slope": 0,
                "intercept": unique_value,
                "r_squared": 1.0,  # Perfectly "fits" the single value
                "fitted_quantiles": [unique_value, unique_value],
                "upper_band": [unique_value, unique_value],
                "lower_band": [unique_value, unique_value],
                "mean": unique_value,
                "median": unique_value,
                "std_dev": 0,
                "variance": 0,
                "skewness": 0,
                "kurtosis": 0,
                "residual_std_error": 0,
                "normality_line": {"x": [unique_value, unique_value], "y": [unique_value, unique_value]},
                "normality_tests": {"Single Value": "Cannot perform normality tests on a single value"}
            }
            continue  # Skip further calculations for single-value columns

        # ✅ Generate theoretical & sample quantiles for normal distribution
        (theoretical_quantiles, sample_quantiles), (slope, intercept, r_value) = stats.probplot(data, dist="norm")

        # ✅ Compute Skewness & Kurtosis
        skewness = stats.skew(data, nan_policy="omit")  
        kurtosis = stats.kurtosis(data, fisher=True, nan_policy="omit")  

        # ✅ Compute Mean, Median, Std Dev, Variance
        mean_value = float(data.mean())
        median_value = float(data.median())
        std_dev = float(data.std())
        variance = std_dev ** 2  

        # ✅ Compute Residual Standard Error (RSE)
        fitted_quantiles = slope * np.array(theoretical_quantiles) + intercept
        residuals = np.array(sample_quantiles) - fitted_quantiles  
        residual_std_error = np.sqrt(np.sum(residuals ** 2) / (len(residuals) - 2))  

        # ✅ Compute Bootstrapped 95% Confidence Bands
        confidence_band = 1.96 * np.std(residuals)  
        upper_band = fitted_quantiles + confidence_band
        lower_band = fitted_quantiles - confidence_band

        # ✅ Compute Min & Max for Normality Line
        min_val = min(theoretical_quantiles)
        max_val = max(theoretical_quantiles)

        # ✅ Normality Tests (Only if std_dev > 0)
        normality_tests = {}
        if std_dev > 0:
            try:
                if len(data) < 5000:
                    shapiro_stat, shapiro_p = stats.shapiro(data)
                    normality_tests["Shapiro-Wilk"] = {"statistic": float(shapiro_stat), "p_value": float(shapiro_p)}
            except Exception as e:
                normality_tests["Shapiro-Wilk"] = f"Error: {str(e)}"

            try:
                anderson_result = stats.anderson(data, dist="norm")
                normality_tests["Anderson-Darling"] = {
                    "statistic": float(anderson_result.statistic),
                    "critical_values": anderson_result.critical_values.tolist(),
                    "significance_levels": anderson_result.significance_level.tolist(),
                }
            except Exception as e:
                normality_tests["Anderson-Darling"] = f"Error: {str(e)}"

            if len(data) >= 5000:
                try:
                    ks_stat, ks_p = stats.kstest(data, "norm", args=(mean_value, std_dev))
                    normality_tests["Kolmogorov-Smirnov"] = {"statistic": float(ks_stat), "p_value": float(ks_p)}
                except Exception as e:
                    normality_tests["Kolmogorov-Smirnov"] = f"Error: {str(e)}"

                try:
                    dagostino_stat, dagostino_p = stats.normaltest(data)
                    normality_tests["D’Agostino-Pearson"] = {"statistic": float(dagostino_stat), "p_value": float(dagostino_p)}
                except Exception as e:
                    normality_tests["D’Agostino-Pearson"] = f"Error: {str(e)}"

            try:
                jb_stat, jb_p = stats.jarque_bera(data)
                normality_tests["Jarque-Bera"] = {"statistic": float(jb_stat), "p_value": float(jb_p)}
            except Exception as e:
                normality_tests["Jarque-Bera"] = f"Error: {str(e)}"

        qq_plot_data[col] = {
            "theoretical_quantiles": theoretical_quantiles.tolist(),
            "sample_quantiles": sample_quantiles.tolist(),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_value**2),
            "fitted_quantiles": fitted_quantiles.tolist(),
            "upper_band": upper_band.tolist(),
            "lower_band": lower_band.tolist(),
            "mean": mean_value,
            "median": median_value,
            "std_dev": std_dev,
            "variance": variance,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "residual_std_error": residual_std_error,
            "normality_line": {"x": [min_val, max_val], "y": [min_val, max_val]},
            "normality_tests": normality_tests
        }

    return jsonify({"session_id": session_id, "qq_plots": qq_plot_data}), 200







