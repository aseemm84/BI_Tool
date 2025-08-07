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
    date_cols = df.select_dtypes(include=['datetime', 'datetimetz']).columns.tolist()
    all_cols = df.columns.tolist()

    # General purpose charts
    if chart_type in ['Line Chart', 'Bar Chart', 'Area Chart', 'Histogram', 'Box Plot', 'Violin Chart']:
        return {'x': categorical_cols + date_cols + numeric_cols, 'y': numeric_cols}

    # Scatter and Bubble charts
    elif chart_type == 'Scatter Plot':
        return {'x': numeric_cols, 'y': numeric_cols, 'color': all_cols, 'size': numeric_cols}
    elif chart_type == '3D Scatter Plot':
        return {'x': numeric_cols, 'y': numeric_cols, 'z': numeric_cols, 'color': all_cols}
    elif chart_type == 'Bubble Chart':
        return {'x': numeric_cols, 'y': numeric_cols, 'size': numeric_cols, 'color': all_cols}

    # Hierarchical charts
    elif chart_type in ['Donut Chart', 'Pie Chart', 'Sunburst Chart', 'Treemap', 'Funnel Chart']:
        return {'names': categorical_cols + date_cols, 'values': numeric_cols, 'path': all_cols}

    # Specialized charts
    elif chart_type == 'Heatmap':
        # Heatmap will typically be a correlation matrix of numeric columns
        return {'numeric_only': numeric_cols}
    elif chart_type == 'Gantt Chart':
        # Gantt charts have very specific requirements
        return {'Task': categorical_cols, 'Start': date_cols, 'Finish': date_cols, 'Color': all_cols}
    elif chart_type == 'Gauge Chart':
        # Gauge charts show single values
        return {'value': numeric_cols, 'threshold': numeric_cols}
    elif chart_type == 'Waterfall Chart':
        # Waterfall charts show cumulative effects
        return {'names': categorical_cols + date_cols, 'values': numeric_cols}

    # For KPI, Data Table, etc.
    else:   
        return {'all': all_cols}

def to_excel(df: pd.DataFrame) -> bytes:
    """
    Converts a dataframe to an in-memory Excel file.
    This is more efficient than writing to disk first.
    """
    output = io.BytesIO()
    # Using xlsxwriter engine allows for more formatting options if needed later.
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Processed_Data')
    processed_data = output.getvalue()
    return processed_data
