import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

def run_full_analysis(df: pd.DataFrame) -> (dict, dict):
    """
    Performs a suite of analyses on the cleaned data.

    Args:
        df: The cleaned pandas DataFrame.

    Returns:
        A tuple containing:
        - A dictionary of analysis results (e.g., correlation matrix).
        - A log dictionary detailing the analysis actions.
    """
    log = {}
    results = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

    # Use an Isolation Forest to flag potential outliers
    if numeric_cols:
        iso_forest = IsolationForest(contamination=0.1, random_state=42)
        outliers = iso_forest.fit_predict(df[numeric_cols])
        results['outliers'] = pd.Series(outliers, index=df.index)
        log['outliers_identified'] = int((outliers == -1).sum())

    # The correlation matrix is fundamental for understanding relationships between variables
    if len(numeric_cols) > 1:
        results['correlation_matrix'] = df[numeric_cols].corr()

    return results, log

def find_key_drivers(df: pd.DataFrame, target_variable: str) -> pd.Series:
    """
    Finds features with the highest correlation to a target variable.

    Args:
        df: The pandas DataFrame.
        target_variable: The column to be used as the target.

    Returns:
        A pandas Series with the top 5 most correlated features.
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if target_variable not in numeric_cols:
        return None
    
    corr_matrix = df[numeric_cols].corr()
    if target_variable in corr_matrix:
        key_drivers = corr_matrix[target_variable].abs().sort_values(ascending=False)
        # Drop the target itself (it will always have a correlation of 1 with itself)
        key_drivers = key_drivers.drop(target_variable).head(5)
        return key_drivers
    return None
