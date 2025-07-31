import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import featuretools as ft

def create_automated_measures(df: pd.DataFrame) -> dict:
    """
    Creates single-value measures from a DataFrame, similar to Power BI measures.

    Args:
        df: The pandas DataFrame.

    Returns:
        A dictionary containing the calculated measures.
    """
    measures = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Create summation and average for numeric columns
    for col in numeric_cols:
        # To avoid adding measures for identifiers or index-like columns with many unique values
        if df[col].nunique() > 1:
            measures[f"Sum of {col}"] = df[col].sum()
            measures[f"Average of {col}"] = df[col].mean()

    # Create distinct count for categorical columns
    for col in categorical_cols:
        measures[f"Count of {col}"] = df[col].nunique()

    return measures

def engineer_features_automated(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Uses featuretools to automatically create new features and calculates single-value measures.

    Args:
        df: The pandas DataFrame.

    Returns:
        A tuple containing:
        - The DataFrame with new features.
        - A log dictionary, including calculated measures.
    """
    log = {}
    initial_feature_count = len(df.columns)
    
    # Calculate automated measures and add them to the log
    log['measures'] = create_automated_measures(df)
    
    es = ft.EntitySet(id='main_entityset')
    df_copy = df.copy()
    if df_copy.index.duplicated().any():
        df_copy = df_copy.reset_index(drop=True)
    df_copy['index_col'] = df_copy.index
    
    es = es.add_dataframe(
        dataframe_name='main_data',
        dataframe=df_copy,
        index='index_col'
    )

    # This part creates new columns (features), which is different from measures
    feature_matrix, _ = ft.dfs(
        entityset=es,
        target_dataframe_name='main_data',
        trans_primitives=['add_numeric', 'multiply_numeric', 'percentile'],
        max_depth=1,
        verbose=False
    )
    
    final_feature_count = len(feature_matrix.columns)
    log['features_engineered'] = final_feature_count - initial_feature_count
    
    return feature_matrix, log

def create_custom_feature(df: pd.DataFrame, definition: dict) -> pd.DataFrame:
    """
    Creates a new feature based on a user-provided definition dictionary.

    Args:
        df: The pandas DataFrame to add the feature to.
        definition: A dictionary defining the feature to create.
    
    Returns:
        The DataFrame with the new feature column.
    """
    op_type = definition.get('type')
    df_out = df.copy()

    try:
        if op_type == 'arithmetic':
            col1, col2, op = definition['col1'], definition['col2'], definition['op']
            new_col_name = f"{col1}_{op}_{col2}"
            if op == 'add':
                df_out[new_col_name] = df_out[col1] + df_out[col2]
            elif op == 'subtract':
                df_out[new_col_name] = df_out[col1] - df_out[col2]
            elif op == 'multiply':
                df_out[new_col_name] = df_out[col1] * df_out[col2]
            elif op == 'divide':
                # Add a small epsilon to avoid division by zero
                df_out[new_col_name] = df_out[col1] / (df_out[col2] + 1e-6)
        
        elif op_type == 'unary':
            col, op = definition['col'], definition['op']
            new_col_name = f"{op}_of_{col}"
            if op == 'log':
                # Add 1 to avoid log(0)
                df_out[new_col_name] = np.log(df_out[col] + 1)
            elif op == 'square':
                df_out[new_col_name] = df_out[col] ** 2
            elif op == 'sqrt':
                df_out[new_col_name] = np.sqrt(df_out[col].clip(lower=0)) # Avoid sqrt of negative
            elif op == 'average':
                # Create a new column where every value is the average of the selected column
                avg_val = df_out[col].mean()
                df_out[new_col_name] = avg_val


        elif op_type == 'categorical_count':
            col = definition['col']
            new_col_name = f"{col}_counts"
            counts = df_out[col].value_counts().to_dict()
            df_out[new_col_name] = df_out[col].map(counts)

    except Exception as e:
        # In a real app, you might want to log this error or show it to the user.
        print(f"Error creating custom feature: {e}")
        return df # Return original df on error

    return df_out


def perform_segmentation(df: pd.DataFrame, n_clusters: int) -> (pd.DataFrame, dict):
    """
    Performs K-Means clustering to segment the data.

    Args:
        df: The pandas DataFrame.
        n_clusters: The number of segments to create.

    Returns:
        A tuple containing:
        - The DataFrame with a new 'Segment' column.
        - A log dictionary.
    """
    log = {}
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    
    if not numeric_cols:
        return df, log

    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_cols])
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Segment'] = kmeans.fit_predict(scaled_data)
    df['Segment'] = df['Segment'].astype('category')
    
    log['segments_created'] = n_clusters
    return df, log
