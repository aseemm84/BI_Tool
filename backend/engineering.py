import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import featuretools as ft

def engineer_features_automated(df: pd.DataFrame) -> (pd.DataFrame, dict):
    """
    Uses featuretools to automatically create new features.

    Args:
        df: The pandas DataFrame.

    Returns:
        A tuple containing:
        - The DataFrame with new features.
        - A log dictionary.
    """
    log = {}
    initial_feature_count = len(df.columns)
    
    # Featuretools requires a unique index
    es = ft.EntitySet(id='main_entityset')
    df_copy = df.copy()
    # Ensure index is unique before setting it
    if df_copy.index.duplicated().any():
        df_copy = df_copy.reset_index(drop=True)
    df_copy['index_col'] = df_copy.index
    
    es = es.add_dataframe(
        dataframe_name='main_data',
        dataframe=df_copy,
        index='index_col'
    )

    # Run Deep Feature Synthesis to generate new features.
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

    # scale data before clustering, so that one feature doesn't dominate the others.
    scaler = StandardScaler()
    scaled_data = scaler.fit_transform(df[numeric_cols])
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df['Segment'] = kmeans.fit_predict(scaled_data)
    df['Segment'] = df['Segment'].astype('category')
    
    log['segments_created'] = n_clusters
    return df, log
