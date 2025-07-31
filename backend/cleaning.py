import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
import janitor  # This is used via the .clean_names() method on the dataframe

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

    # Attempt to convert object columns to datetime where possible
    for col in df.select_dtypes(include=['object']).columns:
        try:
            df[col] = pd.to_datetime(df[col])
        except (ValueError, TypeError):
            # This column is not a date, so we'll just leave it as is.
            pass

    # missing values and imputation
    log['missing_values_filled'] = int(df.isnull().sum().sum())
    
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    for col in numeric_cols:
        df[col].fillna(df[col].mean(), inplace=True)
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

    # convert categorical text columns into numbers
    for col in df.select_dtypes(include=['object']).columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])

    # get rid of any duplicate rows.
    log['duplicates_removed'] = int(df.duplicated().sum())
    df.drop_duplicates(inplace=True)

    return df, log
