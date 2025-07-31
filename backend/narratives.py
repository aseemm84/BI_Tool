import pandas as pd

def generate_narrative(chart_config: dict, df: pd.DataFrame) -> str:
    """
    Generates a one-sentence narrative summary for a given chart and dataframe.

    Args:
        chart_config: The configuration dictionary for the chart.
        df: The pandas DataFrame used for the chart.

    Returns:
        A string containing the automated insight.
    """
    chart_type = chart_config.get('type')

    try:
        if chart_type == 'Bar Chart':
            x_col, y_col = chart_config['x'], chart_config['y']
            if df[x_col].nunique() < 2: return "Not enough distinct categories to compare."
            grouped_data = df.groupby(x_col)[y_col].sum()
            max_cat, min_cat = grouped_data.idxmax(), grouped_data.idxmin()
            return f"The data highlights that '{max_cat}' has the highest value, while '{min_cat}' has the lowest."

        elif chart_type == 'Line Chart':
            x_col, y_col = chart_config['x'], chart_config['y']
            if len(df) < 2: return "Not enough data points to determine a trend."
            start_val, end_val = df[y_col].iloc[0], df[y_col].iloc[-1]
            trend = "an upward trend" if end_val > start_val else "a downward trend" if end_val < start_val else "a stable trend"
            return f"Over the observed period, '{y_col}' shows {trend}."

        elif chart_type in ['Scatter Plot', '3D Scatter Plot', 'Bubble Chart']:
            x_col, y_col = chart_config['x'], chart_config['y']
            correlation = df[x_col].corr(df[y_col])
            strength = "a strong" if abs(correlation) > 0.7 else "a moderate" if abs(correlation) > 0.4 else "a weak"
            direction = "positive" if correlation > 0 else "negative"
            return f"A {strength} {direction} correlation is observed between '{x_col}' and '{y_col}'." if strength != "a weak" else f"There appears to be a weak relationship between '{x_col}' and '{y_col}'."

        elif chart_type in ['Donut Chart', 'Treemap', 'Sunburst Chart']:
            names_col, values_col = chart_config.get('names') or chart_config.get('path')[0], chart_config['values']
            if df[names_col].nunique() < 1: return "No categories to display."
            grouped_data = df.groupby(names_col)[values_col].sum()
            largest_slice = grouped_data.idxmax()
            percentage = (grouped_data.max() / grouped_data.sum()) * 100
            return f"'{largest_slice}' represents the largest segment, accounting for {percentage:.1f}% of the total."
        
        elif chart_type in ['Box Plot', 'Violin Plot']:
            x_col, y_col = chart_config['x'], chart_config['y']
            return f"This plot shows the distribution of '{y_col}' across different categories of '{x_col}', highlighting differences in median and spread."

        elif chart_type == 'Heatmap':
            return "This heatmap visualizes the correlation between numeric variables. Warmer colors indicate a stronger positive correlation."

        else:
            return "This chart visualizes the distribution and relationship of the selected data."

    except Exception:
        return "An automated narrative for this chart could not be generated."
