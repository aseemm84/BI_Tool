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
            # Group by the categorical column and sum the numerical one
            grouped_data = df.groupby(x_col)[y_col].sum()
            max_cat = grouped_data.idxmax()
            min_cat = grouped_data.idxmin()
            return f"The data highlights that '{max_cat}' has the highest value, while '{min_cat}' has the lowest."

        elif chart_type == 'Line Chart':
            x_col, y_col = chart_config['x'], chart_config['y']
            if len(df) < 2: return "Not enough data points to determine a trend."
            # Assuming the x-axis is sorted (e.g., by date)
            start_val = df[y_col].iloc[0]
            end_val = df[y_col].iloc[-1]
            if end_val > start_val:
                trend = "an upward trend"
            elif end_val < start_val:
                trend = "a downward trend"
            else:
                trend = "a stable trend"
            return f"Over the observed period, '{y_col}' shows {trend}."

        elif chart_type == 'Scatter Plot':
            x_col, y_col = chart_config['x'], chart_config['y']
            correlation = df[x_col].corr(df[y_col])
            
            if abs(correlation) > 0.7:
                strength = "a strong"
            elif abs(correlation) > 0.4:
                strength = "a moderate"
            else:
                strength = "a weak"
                
            direction = "positive" if correlation > 0 else "negative"
            
            if strength == "a weak":
                return f"There appears to be a weak relationship between '{x_col}' and '{y_col}'."
            else:
                return f"A {strength} {direction} correlation is observed between '{x_col}' and '{y_col}'."

        elif chart_type == 'Donut Chart':
            names_col, values_col = chart_config['names'], chart_config['values']
            if df[names_col].nunique() < 1: return "No categories to display."
            grouped_data = df.groupby(names_col)[values_col].sum()
            largest_slice = grouped_data.idxmax()
            percentage = (grouped_data.max() / grouped_data.sum()) * 100
            return f"'{largest_slice}' represents the largest segment, accounting for {percentage:.1f}% of the total."

        else:
            # Default message if the chart type has no specific narrative logic yet.
            return "This chart visualizes the distribution and relationship of the selected data."

    except Exception:
        # If any error occurs during narrative generation, just return a safe default.
        return "An automated narrative for this chart could not be generated."
