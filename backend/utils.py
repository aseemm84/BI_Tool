import pandas as pd
import numpy as np
import io

def get_chart_compatible_columns(df: pd.DataFrame, chart_type: str) -> dict:
    """
    Filters and returns columns from the dataframe that are compatible with the selected chart type.
    This helps guide the user to make valid selections.
    """
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    all_cols = df.columns.tolist()

    if chart_type in ['Line Chart', 'Bar Chart', 'Area Chart', 'Histogram', 'Box Plot', 'Violin Plot']:
        return {'x': categorical_cols + date_cols + numeric_cols, 'y': numeric_cols}
    elif chart_type in ['Scatter Plot', 'Bubble Chart']:
        return {'x': numeric_cols, 'y': numeric_cols, 'size': numeric_cols, 'color': all_cols}
    elif chart_type in ['Donut Chart', 'Pie Chart', 'Sunburst Chart', 'Treemap', 'Funnel Chart']:
        return {'names': categorical_cols + date_cols, 'values': numeric_cols}
    else: # For KPI, Data Table, etc.
        return {'all': all_cols}

def to_excel(df: pd.DataFrame) -> bytes:
    """
    Converts a dataframe to an in-memory Excel file.
    This is more efficient than writing to disk first.
    """
    output = io.BytesIO()
    # Using xlsxwriter engine allows for more formatting options if needed later
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Processed_Data')
    processed_data = output.getvalue()
    return processed_data
