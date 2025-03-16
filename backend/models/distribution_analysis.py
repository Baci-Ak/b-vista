import pandas as pd
import numpy as np
import seaborn as sns
from models.data_manager import get_session
from flask import jsonify
from scipy.stats import gaussian_kde
from scipy import stats



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
    Generate QQ-Plot data for selected numeric columns and compute normality tests,
    including 95% confidence bands for the regression fit.

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

        # ✅ Generate theoretical & sample quantiles for normal distribution
        (theoretical_quantiles, sample_quantiles), (slope, intercept, r_value) = stats.probplot(data, dist="norm")

        # ✅ Compute Skewness & Kurtosis
        skewness = stats.skew(data)  # Measures symmetry
        kurtosis = stats.kurtosis(data, fisher=True)  # Measures peak (Fisher=True for normality test)

        # ✅ Compute Mean, Median, Std Dev
        mean_value = float(data.mean())
        median_value = float(data.median())
        std_dev = float(data.std())
        variance = std_dev ** 2  # Variance

        # ✅ Compute Residual Standard Error (RSE)
        fitted_quantiles = slope * np.array(theoretical_quantiles) + intercept  # Compute OLS-fitted values
        residuals = np.array(sample_quantiles) - fitted_quantiles  # Residuals
        residual_std_error = np.sqrt(np.sum(residuals ** 2) / (len(residuals) - 2))  # RSE formula

        # ✅ Compute 95% Confidence Bands
        confidence_band = 1.96 * residual_std_error  # 95% CI multiplier
        upper_band = fitted_quantiles + confidence_band
        lower_band = fitted_quantiles - confidence_band

        # ✅ Compute Min & Max for Normality Line
        min_val = min(theoretical_quantiles)
        max_val = max(theoretical_quantiles)

        # ✅ Normality Tests
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

        # ✅ Jarque-Bera Test (Checks normality using skewness & kurtosis)
        jb_stat, jb_p = stats.jarque_bera(data)
        normality_tests["Jarque-Bera"] = {"statistic": float(jb_stat), "p_value": float(jb_p)}

        qq_plot_data[col] = {
            "theoretical_quantiles": theoretical_quantiles.tolist(),
            "sample_quantiles": sample_quantiles.tolist(),
            "slope": float(slope),
            "intercept": float(intercept),
            "r_squared": float(r_value**2),  # Goodness of fit
            "fitted_quantiles": fitted_quantiles.tolist(),  # Best-fit line points
            "upper_band": upper_band.tolist(),  # ✅ Add Upper Confidence Band
            "lower_band": lower_band.tolist(),  # ✅ Add Lower Confidence Band
            "mean": mean_value,
            "median": median_value,
            "std_dev": std_dev,
            "variance": variance,
            "skewness": skewness,
            "kurtosis": kurtosis,
            "residual_std_error": residual_std_error,
            "normality_line": {
                "x": [min_val, max_val],
                "y": [min_val, max_val]
            },
            "normality_tests": normality_tests  # ✅ Includes multiple normality tests
        }

    return jsonify({
        "session_id": session_id,
        "qq_plots": qq_plot_data
    })








import pandas as pd
import numpy as np
from models.data_manager import get_session
from flask import jsonify


def generate_bar_plot(session_id, group_by_column, measure_column, aggregation="sum", percentage=False, time_grouping=None):
    """
    Generate bar plot data based on a grouping column and numerical column.

    :param session_id: The session ID of the dataset.
    :param group_by_column: The column to group by (categorical, boolean, numeric, or datetime).
    :param measure_column: The numerical column to aggregate.
    :param aggregation: The aggregation method ('sum', 'avg', 'count', 'min', 'max').
    :param percentage: Boolean flag to return values as percentages.
    :param time_grouping: If the group_by_column is datetime, this defines the grouping ('year', 'month', 'week', 'day').
    :return: JSON response with bar plot data.
    """

    session = get_session(session_id)
    if session is None:
        return {"error": "Session not found"}

    df = session["df"].copy()

    # Ensure columns exist
    if group_by_column not in df.columns or measure_column not in df.columns:
        return {"error": "One or more columns not found"}

    # Handle missing values
    df = df[[group_by_column, measure_column]].dropna()

    # Determine column type
    column_dtype = df[group_by_column].dtype

    # Convert boolean to categorical (Yes/No)
    if column_dtype == "bool":
        df[group_by_column] = df[group_by_column].map({True: "Yes", False: "No"})

    # Convert numeric columns to categorical if needed (unique values treated as categories)
    if np.issubdtype(column_dtype, np.number):
        df[group_by_column] = df[group_by_column].astype(str)

    # Handle datetime grouping
    if np.issubdtype(column_dtype, np.datetime64) and time_grouping:
        if time_grouping == "year":
            df[group_by_column] = df[group_by_column].dt.year
        elif time_grouping == "month":
            df[group_by_column] = df[group_by_column].dt.strftime("%Y-%m")
        elif time_grouping == "week":
            df[group_by_column] = df[group_by_column].dt.strftime("%Y-W%W")
        elif time_grouping == "day":
            df[group_by_column] = df[group_by_column].dt.date

    # Perform aggregation
    aggregation_methods = {
        "sum": df.groupby(group_by_column)[measure_column].sum(),
        "avg": df.groupby(group_by_column)[measure_column].mean(),
        "count": df.groupby(group_by_column)[measure_column].count(),
        "min": df.groupby(group_by_column)[measure_column].min(),
        "max": df.groupby(group_by_column)[measure_column].max(),
    }

    if aggregation not in aggregation_methods:
        return {"error": "Invalid aggregation method"}

    grouped_data = aggregation_methods[aggregation].reset_index()

    # Compute percentages if needed
    if percentage:
        total = grouped_data[measure_column].sum()
        grouped_data["percentage"] = (grouped_data[measure_column] / total) * 100

    return jsonify({
        "session_id": session_id,
        "bar_plot": {
            "group_by_column": group_by_column,
            "measure_column": measure_column,
            "aggregation": aggregation,
            "data": grouped_data.to_dict(orient="records")
        }
    })







