import pandas as pd
import numpy as np
import scipy.stats as stats
from statsmodels.imputation.mice import MICEData
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from flask import jsonify
import logging
from bvista.backend.models.data_manager import get_session

logging.basicConfig(level=logging.INFO)


def preprocess_for_numeric_analysis(df):
    """
    Safely select numeric-compatible columns only (excluding timedelta, datetime, etc.).
    """
    safe_df = df.copy()

    # Drop columns with non-numeric types that can't be coerced
    unsupported_types = ['timedelta64[ns]', 'datetime64[ns]', 'object', 'bool']
    safe_df = safe_df.select_dtypes(exclude=unsupported_types)

    # Try converting all remaining to float, drop those that can't
    usable_columns = []
    for col in safe_df.columns:
        try:
            _ = pd.to_numeric(safe_df[col], errors='raise')
            usable_columns.append(col)
        except Exception:
            continue

    return safe_df[usable_columns]


def little_mcar_test(df):
    try:
        df_missing = df.loc[:, df.isnull().sum() > 0]
        if df_missing.empty:
            return {"test": "Little's MCAR", "decision": "No missing data"}

        df_numeric = preprocess_for_numeric_analysis(df_missing)
        categorical_cols = df_missing.select_dtypes(include=["category", "object"]).columns

        # Dummify any usable categorical columns
        if len(categorical_cols) > 0:
            dummies = pd.get_dummies(df_missing[categorical_cols], drop_first=True)
            df_numeric = pd.concat([df_numeric, dummies], axis=1)

        if df_numeric.empty:
            return {"test": "Little's MCAR", "error": "No usable numeric data for test"}

        observed = df_numeric.dropna()
        observed_mean = observed.mean()
        overall_mean = df_numeric.mean()
        observed_cov = observed.cov()

        if observed_cov.empty:
            observed_cov = np.eye(df_numeric.shape[1])

        observed_diag = np.diag(observed_cov) + 1e-10
        chi_stat = np.nansum((observed_mean - overall_mean) ** 2 / observed_diag)
        df_degrees = df_numeric.shape[1]
        p_value = 1 - stats.chi2.cdf(chi_stat, df_degrees)

        decision = "MCAR" if p_value > 0.05 else "Not MCAR"

        return {
            "test": "Little's MCAR",
            "statistic": round(chi_stat, 4),
            "df": df_degrees,
            "p_value": round(p_value, 4),
            "decision": f"{round(p_value, 4)} {'>' if p_value > 0.05 else '<'} 0.05 → {decision}"
        }

    except Exception as e:
        logging.error(f"Error in Little's MCAR test: {e}")
        return {"test": "Little's MCAR", "error": str(e)}


def logistic_regression_mar(df):
    try:
        df_numeric = preprocess_for_numeric_analysis(df)
        if df_numeric.isnull().sum().sum() == 0:
            return {"test": "Logistic Regression", "decision": "No missing data"}

        if df_numeric.shape[1] < 2:
            return {"test": "Logistic Regression", "warning": "Too few usable numeric predictors for MAR detection"}

        missingness_indicator = df_numeric.isnull().any(axis=1).astype(int)
        predictors = df_numeric.fillna(df_numeric.mean())

        scaler = StandardScaler()
        predictors_scaled = scaler.fit_transform(predictors)

        model = LogisticRegression(solver="liblinear")
        model.fit(predictors_scaled, missingness_indicator)

        score = model.score(predictors_scaled, missingness_indicator)
        pseudo_r2 = max(0, 1 - (score / (1 - score + 1e-10)))

        decision = "MAR" if pseudo_r2 > 0.1 else "Likely MCAR"

        return {
            "test": "Logistic Regression (Missingness Model)",
            "statistic": round(pseudo_r2, 4),
            "decision": f"{round(pseudo_r2, 4)} {'>' if pseudo_r2 > 0.1 else '<'} 0.1 → {decision}"
        }

    except Exception as e:
        logging.error(f"Error in Logistic Regression MAR test: {e}")
        return {"test": "Logistic Regression", "error": str(e)}


def expectation_maximization_nmar(df):
    try:
        df_numeric = preprocess_for_numeric_analysis(df)
        if df_numeric.isnull().sum().sum() == 0:
            return {"test": "EM & LRT", "decision": "No missing data"}

        if df_numeric.shape[1] < 2:
            return {"test": "EM & LRT", "warning": "Too few usable numeric predictors for NMAR detection"}

        imp_data = MICEData(df_numeric)
        for _ in range(5):
            imp_data.update_all()

        imputed_df = imp_data.next_sample()
        observed_likelihood = np.nansum(df_numeric.dropna().cov().values)
        full_likelihood = np.nansum(imputed_df.dropna().cov().values)
        likelihood_ratio = -2 * (observed_likelihood - full_likelihood)

        df_degrees = len(df_numeric.columns)
        p_value = 1 - stats.chi2.cdf(likelihood_ratio, df_degrees)

        decision = "NMAR" if p_value < 0.05 else "Likely MAR"

        return {
            "test": "Likelihood-Ratio Test (LRT)",
            "statistic": round(likelihood_ratio, 4),
            "df": df_degrees,
            "p_value": round(p_value, 4),
            "decision": f"{round(p_value, 4)} {'<' if p_value < 0.05 else '>'} 0.05 → {decision}"
        }

    except Exception as e:
        logging.error(f"Error in EM & LRT NMAR test: {e}")
        return {"test": "EM & LRT", "error": str(e)}


def analyze_missing_data_types(session_id, selected_columns=None):
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"})

    df = session["df"].copy()
    if selected_columns:
        df = df[selected_columns]

    if df.isnull().sum().sum() == 0:
        return jsonify({
            "session_id": session_id,
            "results": {
                "MCAR_Test": {"test": "Little's MCAR", "decision": "No missing data"},
                "MAR_Test": {"test": "Logistic Regression", "decision": "No missing data"},
                "NMAR_Test": {"test": "EM & LRT", "decision": "No missing data"},
                "Final_Decision": {"test": "Final Decision", "decision": "No missing data detected"}
            }
        })

    mcar_result = little_mcar_test(df)
    mar_result = logistic_regression_mar(df)
    nmar_result = expectation_maximization_nmar(df)

    decision_weights = {"MCAR": 0, "MAR": 0, "NMAR": 0}
    for result in [mcar_result, mar_result, nmar_result]:
        decision_text = result.get("decision", "")
        if "MCAR" in decision_text:
            decision_weights["MCAR"] += 1
        if "MAR" in decision_text:
            decision_weights["MAR"] += 2
        if "NMAR" in decision_text:
            decision_weights["NMAR"] += 3

    final_decision = max(decision_weights, key=decision_weights.get)

    return jsonify({
        "session_id": session_id,
        "results": {
            "MCAR_Test": mcar_result,
            "MAR_Test": mar_result,
            "NMAR_Test": nmar_result,
            "Final_Decision": {
                "test": "Final Decision",
                "decision": f"Majority Tests Suggest {final_decision}"
            }
        }
    })
