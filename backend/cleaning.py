import pandas as pd
import numpy as np
import janitor  # This is used via the .clean_names() method on the dataframe

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
        # Heuristic 1: Column name suggests it's an ID
        if any(keyword in col.lower() for keyword in ['id', 'no', 'number', 'key', 'code', 'serial']):
            # Heuristic 2: High cardinality (many unique values)
            if df[col].nunique() / len(df) > 0.95:
                useless_cols.append(col)
                continue
        
        # Heuristic 3: All values are unique (likely an index or primary key)
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
    Takes a raw DataFrame and performs all the necessary cleaning steps.

    Args:
        df: The raw pandas DataFrame.

    Returns:
        A tuple containing:
        - The cleaned pandas DataFrame.
        - A log dictionary detailing the cleaning actions.
    """
    # start a log to keep track of what is done.
    log = {}

    # Standardize column names
    df = df.clean_names()

    # NEW: Intelligently remove useless columns first
    df = _remove_useless_columns(df, log)

    # Attempt to convert object columns to datetime where possible
    for col in df.select_dtypes(include=['object']).columns:
        try:
            # Added format='mixed' to handle various date formats more robustly
            df[col] = pd.to_datetime(df[col], format='mixed', errors='coerce')
        except (ValueError, TypeError):
            # This column is not a date, so we'll just leave it as is.
            pass

    # missing values and imputation
    log['missing_values_filled'] = int(df.isnull().sum().sum())
    
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()

    for col in numeric_cols:
        df[col].fillna(df[col].median(), inplace=True) # Using median is more robust to outliers
    
    # --- FIX APPLIED HERE ---
    for col in categorical_cols:
        mode_values = df[col].mode()
        if not mode_values.empty:
            df[col].fillna(mode_values[0], inplace=True)

    for col in datetime_cols:
        mode_values = df[col].mode()
        if not mode_values.empty:
            df[col].fillna(mode_values[0], inplace=True) # Fill with the most frequent date

    # get rid of any duplicate rows.
    log['duplicates_removed'] = int(df.duplicated().sum())
    df.drop_duplicates(inplace=True)

    return df, log
