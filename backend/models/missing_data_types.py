import pandas as pd
import numpy as np
import missingno as msno
import scipy.stats as stats
from statsmodels.imputation.mice import MICEData
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from flask import jsonify
import logging
from models.data_manager import get_session

# Enable logging for debugging
logging.basicConfig(level=logging.INFO)


def little_mcar_test(df):
    """
    Perform Little's MCAR test to determine if missing data is MCAR.
    Returns a test statistic, p-value, and decision.
    """
    try:
        # Remove columns with no missing values
        df_missing = df.loc[:, df.isnull().sum() > 0]

        if df_missing.empty:
            return {"test": "Little's MCAR", "statistic": None, "p_value": None, "decision": "No missing data"}

        # Compute means and covariances for observed/missing data
        observed_means = df_missing.mean()
        missing_means = df_missing[df_missing.isnull().any(axis=1)].mean()

        # Compute covariance matrices
        observed_cov = df_missing.cov()
        missing_cov = df_missing[df_missing.isnull().any(axis=1)].cov()

        # Compute test statistic
        chi_square_stat = np.sum((observed_means - missing_means) ** 2 / observed_cov.diagonal())
        df_degrees = len(df_missing.columns)  # Degrees of freedom
        p_value = 1 - stats.chi2.cdf(chi_square_stat, df_degrees)

        # Decision logic
        decision = "MCAR" if p_value > 0.05 else "Not MCAR"

        return {
            "test": "Little's MCAR",
            "statistic": round(chi_square_stat, 4),
            "df": df_degrees,
            "p_value": round(p_value, 4),
            "decision": f"{round(p_value, 4)} {'>' if p_value > 0.05 else '<'} 0.05 → {decision}"
        }

    except Exception as e:
        logging.error(f"Error in Little's MCAR test: {e}")
        return {"test": "Little's MCAR", "error": str(e)}


def logistic_regression_mar(df, selected_columns):
    """
    Perform Logistic Regression to test if missingness is associated with other variables.
    If missingness is predictable, data is MAR.
    """
    results = []
    try:
        for col in selected_columns:
            if df[col].isnull().sum() == 0:
                continue  # Skip columns with no missing values

            # Create a binary missing indicator for the column
            df["missing_indicator"] = df[col].isnull().astype(int)

            # Select potential predictors (exclude target column)
            predictors = df.drop(columns=[col, "missing_indicator"]).select_dtypes(include=["number"]).dropna()
            if predictors.empty:
                continue  # Skip if no valid predictors

            # Standardize predictors
            scaler = StandardScaler()
            predictors_scaled = scaler.fit_transform(predictors)

            # Fit logistic regression model
            model = LogisticRegression(solver="liblinear")
            model.fit(predictors_scaled, df["missing_indicator"])

            # Compute pseudo R² to measure predictability
            pseudo_r2 = model.score(predictors_scaled, df["missing_indicator"])

            # Decision logic
            decision = "MAR" if pseudo_r2 > 0.1 else "Likely MCAR"

            results.append({
                "column": col,
                "test": "Logistic Regression Missingness",
                "pseudo_r2": round(pseudo_r2, 4),
                "decision": f"{round(pseudo_r2, 4)} {'>' if pseudo_r2 > 0.1 else '<'} 0.1 → {decision}"
            })

        return results

    except Exception as e:
        logging.error(f"Error in Logistic Regression MAR test: {e}")
        return [{"test": "Logistic Regression", "error": str(e)}]


def expectation_maximization_nmar(df, selected_columns):
    """
    Uses Expectation-Maximization (EM) & Likelihood Ratio Test (LRT) to determine if data is NMAR.
    If missing data is systematically different from observed, it is NMAR.
    """
    results = []
    try:
        for col in selected_columns:
            if df[col].isnull().sum() == 0:
                continue  # Skip columns with no missing values

            # Prepare data for MICE (Multiple Imputation by Chained Equations)
            imp_data = MICEData(df.select_dtypes(include=["number"]))
            imp_data.update()

            # Compute likelihood ratio test
            observed_likelihood = imp_data.fit().llf
            full_likelihood = imp_data.data.dropna().cov().sum().sum()
            likelihood_ratio = -2 * (observed_likelihood - full_likelihood)

            # Compute p-value
            df_degrees = len(df.select_dtypes(include=["number"]).columns)
            p_value = 1 - stats.chi2.cdf(likelihood_ratio, df_degrees)

            # Decision logic
            decision = "NMAR" if p_value < 0.05 else "Likely MAR"

            results.append({
                "column": col,
                "test": "EM & Likelihood Ratio Test",
                "statistic": round(likelihood_ratio, 4),
                "df": df_degrees,
                "p_value": round(p_value, 4),
                "decision": f"{round(p_value, 4)} {'<' if p_value < 0.05 else '>'} 0.05 → {decision}"
            })

        return results

    except Exception as e:
        logging.error(f"Error in EM & LRT NMAR test: {e}")
        return [{"test": "EM & LRT", "error": str(e)}]


def analyze_missing_data_types(session_id, selected_columns=None):
    """
    Determines the type of missing data in a dataset using multiple statistical tests.
    Returns structured JSON for frontend rendering.
    """
    # ✅ Retrieve dataset
    session = get_session(session_id)
    if session is None:
        return jsonify({"error": "Session not found"})

    df = session["df"].copy()

    # ✅ Run all tests
    mcar_result = little_mcar_test(df)
    logistic_mar_results = logistic_regression_mar(df, selected_columns or df.columns.tolist())
    em_nmar_results = expectation_maximization_nmar(df, selected_columns or df.columns.tolist())

    # ✅ Format results into a structured JSON response
    return jsonify({
        "session_id": session_id,
        "results": {
            "MCAR_Test": mcar_result,
            "MAR_Tests": logistic_mar_results,
            "NMAR_Tests": em_nmar_results
        }
    })
