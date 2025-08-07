import pandas as pd
import numpy as np
import janitor  # This is used via the .clean_names() method on the dataframe

def _is_likely_date_column(series: pd.Series) -> bool:
    """
    Heuristic to check if an object column is likely to contain dates.
    It checks a sample of the data, and if a high percentage can be parsed
    as a date, it returns True.
    """
    if series.dtype != 'object':
        return False

    # Take a small, random sample to check for date-likeness
    sample = series.dropna().sample(n=min(len(series.dropna()), 20))
    if sample.empty:
        return False

    success_count = 0
    for item in sample:
        try:
            # Try parsing without coercing to see if it's a valid date format
            pd.to_datetime(item)
            success_count += 1
        except (ValueError, TypeError):
            pass

    # If more than 70% of the sample are parsable, assume it's a date column
    return (success_count / len(sample)) > 0.7

def _remove_useless_columns(df: pd.DataFrame, log: dict) -> pd.DataFrame:
    """
    Identifies and removes identifier-like columns from the dataframe.
    Args:
        df: The pandas DataFrame.
        log: The log dictionary to record actions.
    Returns:
        The DataFrame with useless columns removed.
    """
    useless_cols = []

    for col in df.columns:
        # Heuristic 1: High cardinality (many unique values)
        if df[col].nunique() / len(df) > 0.95:
            useless_cols.append(col)
            continue

        # Heuristic 2: All values are unique (likely an index or primary key)
        if df[col].nunique() == len(df):
            useless_cols.append(col)

    if useless_cols:
        df = df.drop(columns=useless_cols)
        log['useless_columns_removed'] = useless_cols
    else:
        log['useless_columns_removed'] = []

    return df

def clean_data(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Takes a raw DataFrame and performs all the necessary cleaning steps in a logical order.
    Args:
        df: The raw pandas DataFrame.
    Returns:
        A tuple containing:
        - The cleaned pandas DataFrame.
        - A log dictionary detailing the cleaning actions.
    """
    log = {}

    # 1. Standardize column names
    df = df.clean_names()

    # 2. Intelligently remove useless columns
    df = _remove_useless_columns(df, log)

    # 3. Get rid of any duplicate rows *before* imputation
    duplicates = int(df.duplicated().sum())
    log['duplicates_removed'] = duplicates
    if duplicates > 0:
        df.drop_duplicates(inplace=True)

    # 4. Smarter datetime conversion
    for col in df.select_dtypes(include=['object']).columns:
        if _is_likely_date_column(df[col]):
            try:
                # errors='coerce' is now safer because we've pre-qualified the column
                df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')
            except (ValueError, TypeError):
                # This should be rare now, but good to have a fallback
                pass

    # 5. Missing values and imputation
    # Calculate missing values *before* filling
    missing_values_count = int(df.isnull().sum().sum())
    log['missing_values_filled'] = missing_values_count

    if missing_values_count > 0:
        numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()

        for col in numeric_cols:
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)

        for col in categorical_cols:
            if df[col].isnull().any():
                mode_values = df[col].mode()
                if not mode_values.empty:
                    df[col].fillna(mode_values[0], inplace=True)

        for col in datetime_cols:
            if df[col].isnull().any():
                mode_values = df[col].mode()
                if not mode_values.empty:
                    df[col].fillna(mode_values[0], inplace=True)

    return df, log
