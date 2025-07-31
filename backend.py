import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.impute import SimpleImputer

def load_data(uploaded_file):
    """
    Loads data from an uploaded CSV file into a pandas DataFrame.
    It's designed to handle potential errors during file reading gracefully.
    """
    if uploaded_file is not None:
        try:
            return pd.read_csv(uploaded_file)
        except Exception as e:
            # Return a descriptive error message if the file can't be parsed.
            return f"Error loading CSV file: {e}"
    return None

def clean_data(df):
    """
    Automatically cleans the DataFrame to prepare it for analysis. This involves:
    1. Removing any duplicate rows to prevent skewed results.
    2. Intelligently converting columns to datetime objects where appropriate.
    3. Filling in missing numerical and categorical data using mean and mode, respectively.
    """
    if not isinstance(df, pd.DataFrame):
        return df
        
    df.drop_duplicates(inplace=True)
    
    # Attempt to convert object columns to datetime format.
    # It only converts if more than half the values are valid dates to avoid incorrect conversions.
    for col in df.select_dtypes(include=['object']).columns:
        try:
            converted_col = pd.to_datetime(df[col], errors='coerce')
            if converted_col.notna().sum() / len(df) > 0.5:
                df[col] = converted_col
        except (ValueError, TypeError):
            # If conversion fails for any reason, just skip to the next column.
            continue

    # Identify numeric columns and fill missing values with the column's average.
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    if numeric_cols:
        imputer = SimpleImputer(strategy='mean')
        df[numeric_cols] = imputer.fit_transform(df[numeric_cols])

    # Identify categorical columns and fill missing values with the most frequent value.
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if categorical_cols:
        imputer = SimpleImputer(strategy='most_frequent')
        df[categorical_cols] = imputer.fit_transform(df[categorical_cols])
        
    return df

def find_best_columns(df):
    """
    Automatically identifies the most likely columns for key dashboard roles (date, metric, category).
    It searches for common names first (e.g., 'sales', 'date') and then falls back to data types.
    """
    cols = df.columns.str.lower()
    
    # Common names to look for in each category.
    date_cols = ['date', 'orderdate', 'timestamp', 'datetime']
    value_cols = ['sales', 'revenue', 'profit', 'amount', 'price']
    category_cols = ['product', 'category', 'item', 'region', 'country', 'city', 'segment']

    # Helper function to find the first matching column name.
    def find_col(possible_names):
        for name in possible_names:
            if name in cols:
                return df.columns[cols.get_loc(name)]
        return None

    best_date = find_col(date_cols)
    best_value = find_col(value_cols)
    best_category = find_col(category_cols)

    # If no common names are found, fall back to the first column of the correct data type.
    if not best_date:
        date_col_list = df.select_dtypes(include=['datetime64[ns]']).columns
        if len(date_col_list) > 0: best_date = date_col_list[0]
    if not best_value:
        numeric_cols_list = df.select_dtypes(include=np.number).columns
        if len(numeric_cols_list) > 0: best_value = numeric_cols_list[0]
    if not best_category:
        cat_cols_list = df.select_dtypes(include=['object', 'category']).columns
        if len(cat_cols_list) > 0: best_category = cat_cols_list[0]
        
    return best_date, best_value, best_category

def calculate_kpis(df, date_col, value_col):
    """
    Calculates high-level Key Performance Indicators for the dashboard header.
    Includes total value, average value, transaction count, and Year-over-Year growth if possible.
    """
    if not value_col or value_col not in df.columns:
        return {}
    
    total_value = df[value_col].sum()
    avg_value = df[value_col].mean()
    
    kpis = {
        "Total Revenue/Value": f"${total_value:,.2f}",
        "Average Transaction Value": f"${avg_value:,.2f}",
        "Total Transactions": f"{len(df):,}"
    }
    
    # Calculate Year-over-Year growth if there's enough historical data.
    if date_col and date_col in df.columns:
        df_time = df.set_index(date_col)
        yearly_sales = df_time[value_col].resample('Y').sum()
        if len(yearly_sales) > 1:
            yoy_growth = yearly_sales.pct_change().iloc[-1] * 100
            kpis['Year-over-Year Growth'] = f"{yoy_growth:.2f}%"
            
    return kpis

def get_contribution_analysis(df, category_col, value_col):
    """
    Analyzes the contribution of different categories to the total value,
    which is perfect for creating donut charts or Pareto analysis.
    """
    if not category_col or not value_col or category_col not in df.columns or value_col not in df.columns:
        return None
    
    contribution = df.groupby(category_col)[value_col].sum().sort_values(ascending=False).reset_index()
    return contribution

def get_time_series_decomposition(df, date_col, value_col):
    """
    Decomposes a time series into its trend, seasonal, and residual components.
    This helps in understanding the underlying patterns in the data over time.
    """
    if not date_col or not value_col or date_col not in df.columns or value_col not in df.columns:
        return None
        
    # Resample data to a monthly frequency for stable decomposition.
    df_resampled = df.set_index(date_col)[value_col].resample('M').sum()
    
    # Decomposition requires at least two full seasonal cycles (24 months).
    if len(df_resampled) < 24:
        return None
        
    decomposition = seasonal_decompose(df_resampled, model='additive', period=12)
    return decomposition
