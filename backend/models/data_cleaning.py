import pandas as pd
import numpy as np
from flask import jsonify
from models.data_manager import get_session, add_session
from sklearn.impute import SimpleImputer
from sklearn.impute import KNNImputer  

from sklearn.experimental import enable_iterative_imputer  # noqa
from sklearn.impute import IterativeImputer

from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score







# ✅ Convert all values to JSON-safe format

def make_json_safe(val):
    try:
        if pd.isna(val):
            return None
        elif isinstance(val, (pd.Timestamp, pd.Timedelta, np.datetime64)):
            return str(val)
        elif isinstance(val, (dict, list, tuple, np.ndarray)):
            return str(val)  # ⛔️ Convert arrays/lists/dicts to string instead of returning raw
        elif isinstance(val, (np.generic, np.bool_)):
            return val.item()
        return val
    except Exception as e:
        return str(val)  # Fallback: stringify unknown objects








def drop_missing_data(session_id, columns=None):
    """
    Drops rows with missing values in specified columns or the entire dataset.
    Handles mixed datatypes, ensures valid columns, and returns consistent metadata.

    Parameters:
        session_id (str): ID of the dataset session.
        columns (list, optional): Columns to check for missing data.

    Returns:
        JSON: Response with cleaned data, status message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)


     # ✅ Normalize common "null-ish" values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a", ],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate selected columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
    else:
        columns = all_columns  # Drop rows with any missing value across all columns

    # ✅ Count rows before drop
    original_row_count = df_cleaned.shape[0]

    # ✅ Drop rows with missing values in specified columns
    df_cleaned = df_cleaned.dropna(subset=columns)
    cleaned_row_count = df_cleaned.shape[0]
    rows_dropped = original_row_count - cleaned_row_count

    # ✅ Update session
    add_session(session_id, df_cleaned.copy(), session.get("name"))

    # ✅ Prepare cleaned data
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build message
    if rows_dropped == 0:
        msg = "✅ No missing data found. Nothing dropped."
    else:
        msg = f"🧹 Dropped {rows_dropped} row(s) with missing values."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_dropped": rows_dropped,
        "total_rows": cleaned_row_count,
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200









def impute_with_mean(session_id, columns=None):
    """
    Imputes missing numeric values using column-wise mean.

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to impute. If None, all numeric columns are used.

    Returns:
        JSON response with imputed data, summary message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

      # ✅ Normalize common "null-ish" values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a", ],
        value=np.nan,
        inplace=True
    )
    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate selected columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
    else:
        columns = all_columns  # Use all columns if none provided

    # ✅ Identify numeric columns
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()

    # ✅ Filter only selected numeric columns
    selected_numeric_cols = [col for col in columns if col in numeric_cols]
    skipped_cols = [col for col in columns if col not in numeric_cols]

    if not selected_numeric_cols:
        return jsonify({"error": "No numeric columns selected. Please choose numeric columns only."}), 400

    # ✅ Count missing values before imputation
    missing_before = df_cleaned[selected_numeric_cols].isna().sum().sum()

    if missing_before == 0:
        msg = "✅ Filled 0 missing value(s). No missing values were found."
        if skipped_cols:
            msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
        return jsonify({
            "session_id": session_id,
            "message": msg,
            "rows_imputed": 0,
            "total_rows": df_cleaned.shape[0],
            "total_columns": df_cleaned.shape[1],
            "data": df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")
        }), 200

    # ✅ Perform imputation
    imputer = SimpleImputer(strategy="mean")
    df_cleaned[selected_numeric_cols] = imputer.fit_transform(df_cleaned[selected_numeric_cols])

    # ✅ Recalculate missing values
    missing_after = df_cleaned[selected_numeric_cols].isna().sum().sum()
    values_filled = int(missing_before - missing_after)

    # ✅ Save updated session
    add_session(session_id, df_cleaned.copy(), session.get("name"))

    # ✅ Prepare clean data
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build message
    msg = f"✅ Filled {values_filled} missing value(s) using column mean."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": values_filled,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200










def impute_with_median(session_id, columns=None):
    """
    Imputes missing numeric values using column-wise median.

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to impute. If None, all numeric columns are used.

    Returns:
        JSON response with imputed data, summary message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

     # ✅ Normalize common "null-ish" values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a", ],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate selected columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
    else:
        columns = all_columns  # Use all columns if none provided

    # ✅ Identify numeric columns
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()

    # ✅ Filter only selected numeric columns
    selected_numeric_cols = [col for col in columns if col in numeric_cols]
    skipped_cols = [col for col in columns if col not in numeric_cols]

    if not selected_numeric_cols:
        return jsonify({"error": "No numeric columns selected. Please choose numeric columns only."}), 400

    # ✅ Count missing values before imputation
    missing_before = df_cleaned[selected_numeric_cols].isna().sum().sum()

    if missing_before == 0:
        msg = "✅ Filled 0 missing value(s). No missing values were found."
        if skipped_cols:
            msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
        return jsonify({
            "session_id": session_id,
            "message": msg,
            "rows_imputed": 0,
            "total_rows": df_cleaned.shape[0],
            "total_columns": df_cleaned.shape[1],
            "data": df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")
        }), 200

    # ✅ Perform median imputation
    imputer = SimpleImputer(strategy="median")
    df_cleaned[selected_numeric_cols] = imputer.fit_transform(df_cleaned[selected_numeric_cols])

    # ✅ Recalculate missing values
    missing_after = df_cleaned[selected_numeric_cols].isna().sum().sum()
    values_filled = int(missing_before - missing_after)

    # ✅ Save updated session
    add_session(session_id, df_cleaned.copy(), session.get("name"))

    # ✅ Prepare clean data
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build message
    msg = f"✅ Filled {values_filled} missing value(s) using column median."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": values_filled,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200






def impute_with_mode(session_id, columns=None):
    """
    Imputes missing values using the most frequent value (mode) for selected columns.
    Skips columns with complex types or those that can't be safely imputed.

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to impute. If None, all columns are considered.

    Returns:
        JSON: Imputed dataset and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

     # ✅ Normalize common "null-ish" values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a", ],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate selected columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = [col for col in columns if col in all_columns]
    else:
        selected_cols = all_columns

    if not selected_cols:
        return jsonify({"error": "No columns available for mode imputation."}), 400

    rows_imputed = 0
    imputed_columns = []
    skipped_columns = []

    for col in selected_cols:
        series = df_cleaned[col]

        # ✅ Skip complex types (list, dict, array, tuple, ndarray)
        try:
            if series.dropna().apply(lambda x: isinstance(x, (list, dict, tuple, np.ndarray))).any():
                skipped_columns.append(col)
                continue
        except Exception:
            skipped_columns.append(col)
            continue

        # ✅ Skip if no missing values
        if series.isna().sum() == 0:
            continue

        try:
            mode_series = series.dropna().mode()
            if mode_series.empty:
                skipped_columns.append(col)
                continue

            mode_value = mode_series.iloc[0]
            impute_count = int(series.isna().sum())

            df_cleaned[col] = series.fillna(mode_value)
            rows_imputed += impute_count
            imputed_columns.append(col)

        except Exception:
            skipped_columns.append(col)
            continue

    # ✅ Update session with cleaned data
    add_session(session_id, df_cleaned.copy(), session["name"])

    # ✅ Format for frontend
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build final message
    if rows_imputed == 0:
        msg = "⚠️ No missing values were imputed. All values may already be filled or columns were incompatible."
    else:
        msg = f"✅ Filled {rows_imputed} missing value(s) using column mode."

    if skipped_columns:
        msg += f" ⚠️ Skipped {len(skipped_columns)} column(s): {skipped_columns}"

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200






def impute_with_forward_fill(session_id, columns=None):
    """
    Fills missing values using forward fill (propagates last valid value forward).

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to apply forward fill. Defaults to all.

    Returns:
        JSON response with imputed data, summary message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Normalize null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    rows_imputed = 0
    imputed_columns = []
    skipped_columns = []
    completely_null_columns = []

    for col in selected_cols:
        if df_cleaned[col].isna().sum() == 0:
            continue  # No missing values

        # Check if column is entirely null (can't forward fill at all)
        if df_cleaned[col].notna().sum() == 0:
            completely_null_columns.append(col)
            continue

        filled_before = df_cleaned[col].isna().sum()
        df_cleaned[col] = df_cleaned[col].ffill()
        filled_after = df_cleaned[col].isna().sum()
        filled = int(filled_before - filled_after)

        if filled > 0:
            rows_imputed += filled
            imputed_columns.append(col)
        else:
            skipped_columns.append(col)

    # ✅ Update session
    add_session(session_id, df_cleaned.copy(), session["name"])

    # ✅ Prepare output
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Message builder
    if rows_imputed == 0:
        msg = "⚠️ No values were forward filled."
        if completely_null_columns:
            msg += f" Columns entirely null: {completely_null_columns}."
        if skipped_columns:
            msg += f" Columns unchanged: {skipped_columns}."
    else:
        msg = f"➡️ Forward filled {rows_imputed} missing value(s) across {len(imputed_columns)} column(s)."
        if completely_null_columns:
            msg += f" ⚠️ Skipped {len(completely_null_columns)} column(s) with only nulls: {completely_null_columns}."
        if skipped_columns:
            msg += f" ⚠️ {len(skipped_columns)} column(s) had no fillable values: {skipped_columns}."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "skipped_columns": skipped_columns,
        "null_only_columns": completely_null_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200








def impute_with_backward_fill(session_id, columns=None):
    """
    Fills missing values using backward fill (uses next valid value to fill gaps).

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to apply backward fill. Defaults to all.

    Returns:
        JSON response with imputed data, summary message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404
    
    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400
    
    df_cleaned = df.copy(deep=True)
    
    # ✅ Normalize known null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )
    
    all_columns = df_cleaned.columns.tolist()
    
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
    else:
        columns = all_columns
    
    rows_imputed = 0
    imputed_columns = []
    
    for col in columns:
        if df_cleaned[col].isna().sum() == 0:
            continue

        filled_before = df_cleaned[col].isna().sum()
        df_cleaned[col] = df_cleaned[col].bfill()
        filled_after = df_cleaned[col].isna().sum()
        filled = int(filled_before - filled_after)

        if filled > 0:
            rows_imputed += filled
            imputed_columns.append(col)
    
    # ✅ Update session
    add_session(session_id, df_cleaned.copy(), session["name"])
    
    # ✅ Prepare cleaned data
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")


    
    # ✅ Compose message
    if rows_imputed == 0:
        msg = "✅ No missing values found to fill using backward fill."
    else:
        msg = f"⬅️ Backward filled {rows_imputed} missing value(s) across {len(imputed_columns)} column(s)."
    
    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200










def impute_with_interpolation(session_id, columns=None):
    """
    Imputes missing values using linear interpolation for numeric and datetime columns.

    Parameters:
        session_id (str): Session ID of the dataset.
        columns (list, optional): Columns to interpolate. Defaults to all interpolatable columns.

    Returns:
        JSON response with interpolated data, summary message, and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Normalize null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate columns
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    interpolatable_cols = df_cleaned.select_dtypes(include=[np.number, 'datetime64']).columns.tolist()

    selected_interpolatable = [col for col in selected_cols if col in interpolatable_cols]
    skipped_cols = [col for col in selected_cols if col not in interpolatable_cols]

    if not selected_interpolatable:
        return jsonify({"error": "No supported columns selected. Only numeric and datetime columns are supported for interpolation."}), 400

    rows_imputed = 0
    imputed_columns = []
    unchanged_columns = []

    for col in selected_interpolatable:
        if df_cleaned[col].isna().sum() == 0:
            continue  # Nothing to interpolate

        before = df_cleaned[col].isna().sum()
        try:
            df_cleaned[col] = df_cleaned[col].interpolate(method='linear', limit_direction='both')
            after = df_cleaned[col].isna().sum()
            filled = int(before - after)

            if filled > 0:
                rows_imputed += filled
                imputed_columns.append(col)
            else:
                unchanged_columns.append(col)
        except Exception:
            skipped_cols.append(col)

    # ✅ Update session
    add_session(session_id, df_cleaned.copy(), session["name"])

    # ✅ Prepare data for frontend
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build final message
    if rows_imputed == 0:
        msg = "⚠️ No values were interpolated. Columns may already be filled or unsupported."
    else:
        msg = f"🔁 Interpolated {rows_imputed} missing value(s) across {len(imputed_columns)} column(s)."

    if unchanged_columns:
        msg += f" ⚠️ No change in {len(unchanged_columns)} column(s)."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} unsupported or failed column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "skipped_columns": skipped_cols,
        "unchanged_columns": unchanged_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200








def impute_with_spline(session_id, columns=None, order=3):
    """
    Imputes missing values using spline interpolation (default cubic) for numeric columns.

    Parameters:
        session_id (str): ID of the dataset session.
        columns (list, optional): List of columns to interpolate.
        order (int): Degree of the spline polynomial (default = 3 for cubic).

    Returns:
        JSON: Cleaned dataset and metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Normalize null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]

    if not selected_numeric:
        return jsonify({"error": "No numeric columns selected. Spline interpolation only supports numeric data."}), 400

    rows_imputed = 0
    imputed_columns = []
    failed_columns = []

    for col in selected_numeric:
        if df_cleaned[col].isna().sum() == 0:
            continue

        try:
            before = df_cleaned[col].isna().sum()
            df_cleaned[col] = df_cleaned[col].interpolate(method="spline", order=order, limit_direction="both")
            after = df_cleaned[col].isna().sum()
            filled = int(before - after)
            if filled > 0:
                rows_imputed += filled
                imputed_columns.append(col)
            else:
                failed_columns.append(col)
        except Exception as e:
            failed_columns.append(col)

    add_session(session_id, df_cleaned.copy(), session["name"])

    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    msg = f"🧮 Spline interpolated {rows_imputed} value(s) across {len(imputed_columns)} column(s)."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
    if failed_columns:
        msg += f" ❌ Interpolation failed in {len(failed_columns)} column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "skipped_columns": skipped_cols,
        "failed_columns": failed_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200





# Advanced interpolation method with polynomial interpolation
def impute_with_polynomial(session_id, columns=None, order=2):
    """
    Imputes missing values using polynomial interpolation for numeric columns.

    Parameters:
        session_id (str): Dataset session ID.
        columns (list, optional): Columns to interpolate.
        order (int): Degree of polynomial (default = 2 for quadratic).

    Returns:
        JSON: Cleaned data and response metadata.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Normalize missing
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]

    if not selected_numeric:
        return jsonify({"error": "No numeric columns selected. Polynomial interpolation only supports numeric data."}), 400

    rows_imputed = 0
    imputed_columns = []
    failed_columns = []

    for col in selected_numeric:
        if df_cleaned[col].isna().sum() == 0:
            continue

        try:
            before = df_cleaned[col].isna().sum()
            df_cleaned[col] = df_cleaned[col].interpolate(method="polynomial", order=order, limit_direction="both")
            after = df_cleaned[col].isna().sum()
            filled = int(before - after)

            if filled > 0:
                rows_imputed += filled
                imputed_columns.append(col)
            else:
                failed_columns.append(col)
        except Exception:
            failed_columns.append(col)

    add_session(session_id, df_cleaned.copy(), session["name"])

    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    msg = f"📐 Polynomial interpolated {rows_imputed} value(s) across {len(imputed_columns)} column(s)."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
    if failed_columns:
        msg += f" ❌ Interpolation failed in {len(failed_columns)} column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "skipped_columns": skipped_cols,
        "failed_columns": failed_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200



# 🔍 Fill missing values using K-Nearest Neighbors (KNN) Imputation
def impute_with_knn(session_id, columns=None, n_neighbors=5):
    """
    Imputes missing values using K-Nearest Neighbors for numeric columns.

    Parameters:
        session_id (str): Dataset session ID.
        columns (list, optional): Columns to apply KNN imputation. Defaults to all numeric.
        n_neighbors (int): Number of neighbors to use for imputation (default=5).

    Returns:
        JSON: Cleaned data and metadata.
    """
    

    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Standardize null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    # ✅ Validate column selection
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    # ✅ Focus only on numeric columns for KNN
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]

    if not selected_numeric:
        return jsonify({"error": "KNN imputation requires numeric columns. No compatible columns found."}), 400

    # ✅ Keep track of original missing values
    missing_before = df_cleaned[selected_numeric].isna().sum().sum()

    if missing_before == 0:
        msg = "✅ No missing values found. Nothing to impute."
        if skipped_cols:
            msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
        return jsonify({
            "session_id": session_id,
            "message": msg,
            "rows_imputed": 0,
            "imputed_columns": selected_numeric,
            "skipped_columns": skipped_cols,
            "total_rows": df_cleaned.shape[0],
            "total_columns": df_cleaned.shape[1],
            "data": df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")
        }), 200

    try:
        # ✅ KNN Imputation
        imputer = KNNImputer(n_neighbors=n_neighbors)
        df_cleaned[selected_numeric] = imputer.fit_transform(df_cleaned[selected_numeric])
    except Exception as e:
        return jsonify({"error": f"KNN imputation failed due to: {str(e)}"}), 500

    # ✅ Post-imputation stats
    missing_after = df_cleaned[selected_numeric].isna().sum().sum()
    values_filled = int(missing_before - missing_after)

    # ✅ Save updated session
    add_session(session_id, df_cleaned.copy(), session.get("name"))

    # ✅ Prepare JSON-safe output
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    # ✅ Build final message
    msg = f"🤖 KNN imputed {values_filled} missing value(s) across {len(selected_numeric)} numeric column(s)."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": values_filled,
        "imputed_columns": selected_numeric,
        "skipped_columns": skipped_cols,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200








# 🔁 Fill missing values using Iterative Imputer (MICE)
def impute_with_iterative(session_id, columns=None, max_iter=10):
    """
    Imputes missing values using Iterative Imputer (MICE) for numeric columns.

    Parameters:
        session_id (str): Dataset session ID.
        columns (list, optional): Columns to apply iterative imputation. Defaults to all numeric.
        max_iter (int): Maximum number of imputation iterations.

    Returns:
        JSON: Cleaned data and metadata.
    """
    

    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    # ✅ Normalize null-ish values
    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()

    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    # ✅ Filter numeric columns
    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]

    if not selected_numeric:
        return jsonify({"error": "No numeric columns selected. Iterative imputation supports only numeric data."}), 400

    missing_before = df_cleaned[selected_numeric].isna().sum().sum()

    if missing_before == 0:
        msg = "✅ No missing values found. Nothing to impute."
        if skipped_cols:
            msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
        return jsonify({
            "session_id": session_id,
            "message": msg,
            "rows_imputed": 0,
            "imputed_columns": selected_numeric,
            "skipped_columns": skipped_cols,
            "total_rows": df_cleaned.shape[0],
            "total_columns": df_cleaned.shape[1],
            "data": df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")
        }), 200

    try:
        imputer = IterativeImputer(max_iter=max_iter, random_state=0)
        df_cleaned[selected_numeric] = imputer.fit_transform(df_cleaned[selected_numeric])
    except Exception as e:
        return jsonify({"error": f"Iterative imputation failed due to: {str(e)}"}), 500

    missing_after = df_cleaned[selected_numeric].isna().sum().sum()
    values_filled = int(missing_before - missing_after)

    add_session(session_id, df_cleaned.copy(), session.get("name"))

    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    msg = f"🔁 Iterative imputed {values_filled} value(s) across {len(selected_numeric)} numeric column(s) using max_iter=10."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": values_filled,
        "imputed_columns": selected_numeric,
        "skipped_columns": skipped_cols,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200








# Fill missing values using Regression Imputation
def impute_with_regression(session_id, columns=None):
    """
    Imputes missing values using regression-based prediction.
    Only numeric columns are supported. Each target column is imputed
    by predicting missing values using all other available features.

    Parameters:
        session_id (str): Session identifier.
        columns (list, optional): Columns to impute. Defaults to all numeric.

    Returns:
        JSON: Cleaned data and response message.
    """
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404

    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)

    df_cleaned.replace(
        to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a"],
        value=np.nan,
        inplace=True
    )

    all_columns = df_cleaned.columns.tolist()
    if columns:
        missing_cols = [col for col in columns if col not in all_columns]
        if missing_cols:
            return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400
        selected_cols = columns
    else:
        selected_cols = all_columns

    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]

    if not selected_numeric:
        return jsonify({"error": "No numeric columns selected. Regression imputation supports only numeric data."}), 400

    rows_imputed = 0
    imputed_columns = []
    failed_columns = []

    for target in selected_numeric:
        if df_cleaned[target].isna().sum() == 0:
            continue

        # Use other numeric columns as predictors
        predictors = [col for col in numeric_cols if col != target and df_cleaned[col].isna().sum() == 0]
        if len(predictors) < 1:
            failed_columns.append(target)
            continue

        try:
            known = df_cleaned[df_cleaned[target].notna()][predictors + [target]].dropna()
            unknown = df_cleaned[df_cleaned[target].isna()][predictors].dropna()

            if known.empty or unknown.empty:
                failed_columns.append(target)
                continue

            X_train = known[predictors]
            y_train = known[target]
            X_pred = unknown

            model = LinearRegression()
            model.fit(X_train, y_train)
            predicted_values = model.predict(X_pred)

            df_cleaned.loc[unknown.index, target] = predicted_values
            rows_imputed += len(predicted_values)
            imputed_columns.append(target)

        except Exception:
            failed_columns.append(target)
            continue

    add_session(session_id, df_cleaned.copy(), session["name"])
    json_data = df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")

    msg = f"📈 Regression imputed {rows_imputed} missing value(s) across {len(imputed_columns)} column(s)."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
    if failed_columns:
        msg += f" ❌ Failed on {len(failed_columns)} column(s): {failed_columns}"

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": rows_imputed,
        "imputed_columns": imputed_columns,
        "skipped_columns": skipped_cols,
        "failed_columns": failed_columns,
        "total_rows": df_cleaned.shape[0],
        "total_columns": df_cleaned.shape[1],
        "data": json_data
    }), 200







def impute_with_autoencoder(session_id, columns=None, epochs=100):
    """
    Imputes missing values using a Deep Autoencoder (neural net reconstruction).
    
    Parameters:
        session_id (str): Dataset session ID.
        columns (list, optional): Columns to apply Autoencoder imputation. Defaults to all numeric.
        epochs (int): Training epochs for autoencoder. Default is 100.

    Returns:
        JSON: Cleaned dataset and metadata.
    """
    try:
        import torch
        import torch.nn as nn
        from torch.utils.data import DataLoader, TensorDataset
    except ImportError:
        return jsonify({"error": "PyTorch is not installed. Run 'pip install torch'."}), 500

    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found."}), 404
    df = session.get("df")
    if df is None or df.empty:
        return jsonify({"error": "Dataset is empty or unavailable."}), 400

    df_cleaned = df.copy(deep=True)
    df_cleaned.replace(to_replace=["", " ", "NaN", "nan", "None", "NULL", "null", "NaT", "N/A", "n/a", np.inf, -np.inf], value=np.nan, inplace=True)

    all_columns = df_cleaned.columns.tolist()
    selected_cols = columns if columns else all_columns
    missing_cols = [col for col in selected_cols if col not in all_columns]
    if missing_cols:
        return jsonify({"error": f"Column(s) not found: {missing_cols}"}), 400

    numeric_cols = df_cleaned.select_dtypes(include=[np.number]).columns.tolist()
    selected_numeric = [col for col in selected_cols if col in numeric_cols]
    skipped_cols = [col for col in selected_cols if col not in numeric_cols]
    if not selected_numeric:
        return jsonify({"error": "No numeric columns selected. Autoencoder supports numeric data only."}), 400

    cols_with_missing = [col for col in selected_numeric if df_cleaned[col].isna().sum() > 0]
    if not cols_with_missing:
        msg = "✅ No missing values found. Nothing to impute."
        if skipped_cols:
            msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."
        return jsonify({
            "session_id": session_id,
            "message": msg,
            "rows_imputed": 0,
            "imputed_columns": [],
            "skipped_columns": skipped_cols,
            "total_rows": df_cleaned.shape[0],
            "total_columns": df_cleaned.shape[1],
            "data": df_cleaned.where(pd.notna(df_cleaned), None).applymap(make_json_safe).to_dict(orient="records")
        }), 200

    # Simple normalization
    data = df_cleaned[selected_numeric]
    impute_values = data.mean()
    data = data.fillna(impute_values)
    X = torch.tensor(data.values, dtype=torch.float32)

    # Build Autoencoder
    class Autoencoder(nn.Module):
        def __init__(self, input_dim):
            super().__init__()
            self.encoder = nn.Sequential(nn.Linear(input_dim, input_dim // 2), nn.ReLU(), nn.Linear(input_dim // 2, input_dim // 4), nn.ReLU())
            self.decoder = nn.Sequential(nn.Linear(input_dim // 4, input_dim // 2), nn.ReLU(), nn.Linear(input_dim // 2, input_dim))

        def forward(self, x): return self.decoder(self.encoder(x))

    try:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model = Autoencoder(X.shape[1]).to(device)
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

        dataset = DataLoader(TensorDataset(X), batch_size=32, shuffle=True)
        model.train()
        for epoch in range(epochs):
            for batch in dataset:
                batch_x = batch[0].to(device)
                output = model(batch_x)
                loss = criterion(output, batch_x)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

        # Reconstruction
        model.eval()
        with torch.no_grad():
            X_reconstructed = model(X.to(device)).cpu().numpy()

        df_imputed = df_cleaned.copy()
        df_imputed[selected_numeric] = np.where(df_cleaned[selected_numeric].isna(), X_reconstructed, df_cleaned[selected_numeric].values)

    except Exception as e:
        return jsonify({"error": f"Autoencoder imputation failed: {str(e)}"}), 500

    values_filled = df_cleaned[selected_numeric].isna().sum().sum()
    add_session(session_id, df_imputed.copy(), session.get("name"))

    json_data = df_imputed.where(pd.notna(df_imputed), None).applymap(make_json_safe).to_dict(orient="records")
    msg = f"🧠 Autoencoder filled {int(values_filled)} missing value(s) across {len(cols_with_missing)} column(s) using {epochs} training epochs."
    if skipped_cols:
        msg += f" ⚠️ Skipped {len(skipped_cols)} non-numeric column(s)."

    return jsonify({
        "session_id": session_id,
        "message": msg,
        "rows_imputed": int(values_filled),
        "imputed_columns": cols_with_missing,
        "skipped_columns": skipped_cols,
        "total_rows": df_imputed.shape[0],
        "total_columns": df_imputed.shape[1],
        "data": json_data
    }), 200

















