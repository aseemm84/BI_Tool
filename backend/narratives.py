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
            x_col, y_col = chart_config.get('x'), chart_config.get('y')
            if not x_col or not y_col or df[x_col].nunique() < 2: 
                return "Not enough distinct categories to compare."

            grouped_data = df.groupby(x_col)[y_col].sum()
            max_cat, min_cat = grouped_data.idxmax(), grouped_data.idxmin()
            return f"The data highlights that '{max_cat}' has the highest value, while '{min_cat}' has the lowest."

        elif chart_type in ['Line Chart', 'Area Chart']:
            x_col, y_col = chart_config.get('x'), chart_config.get('y')
            if not x_col or not y_col or len(df) < 2: 
                return "Not enough data points to determine a trend."

            start_val, end_val = df[y_col].iloc[0], df[y_col].iloc[-1]
            trend = "an upward trend" if end_val > start_val else "a downward trend" if end_val < start_val else "a stable trend"
            return f"Over the observed period, '{y_col}' shows {trend}."

        elif chart_type in ['Scatter Plot', '3D Scatter Plot', 'Bubble Chart']:
            x_col, y_col = chart_config.get('x'), chart_config.get('y')
            if not x_col or not y_col: 
                return "X and Y axes must be selected."

            correlation = df[x_col].corr(df[y_col])
            strength = "a strong" if abs(correlation) > 0.7 else "a moderate" if abs(correlation) > 0.4 else "a weak"
            direction = "positive" if correlation > 0 else "negative"
            return f"A {strength} {direction} correlation is observed between '{x_col}' and '{y_col}'." if strength != "a weak" else f"There appears to be a weak relationship between '{x_col}' and '{y_col}'."

        elif chart_type in ['Donut Chart', 'Pie Chart', 'Treemap', 'Sunburst Chart']:
            names_col = chart_config.get('names') or (chart_config.get('path') and chart_config.get('path')[0])
            values_col = chart_config.get('values')
            if not names_col or not values_col or df[names_col].nunique() < 1: 
                return "No categories to display."

            grouped_data = df.groupby(names_col)[values_col].sum()
            largest_slice = grouped_data.idxmax()
            percentage = (grouped_data.max() / grouped_data.sum()) * 100 
            return f"'{largest_slice}' represents the largest segment, accounting for {percentage:.1f}% of the total."

        elif chart_type == 'Funnel Chart':
            names_col, values_col = chart_config.get('names'), chart_config.get('values')
            if not names_col or not values_col or df[names_col].nunique() < 1: 
                return "No categories to display."

            # Assuming the dataframe is sorted for the funnel stages
            df_sorted = df.sort_values(by=values_col, ascending=False)
            initial_stage_val = df_sorted[values_col].iloc[0]
            final_stage_val = df_sorted[values_col].iloc[-1]
            conversion_rate = (final_stage_val / initial_stage_val) * 100 if initial_stage_val > 0 else 0
            return f"The funnel shows a conversion from '{df_sorted[names_col].iloc[0]}' to '{df_sorted[names_col].iloc[-1]}', with an overall conversion rate of {conversion_rate:.1f}%."

        elif chart_type in ['Box Plot', 'Violin Chart']:
            x_col, y_col = chart_config.get('x'), chart_config.get('y')
            if not x_col or not y_col: 
                return "X and Y axes must be selected."
            return f"This plot shows the distribution of '{y_col}' across different categories of '{x_col}', highlighting differences in median and spread."

        elif chart_type == 'Heatmap':
            return "This heatmap visualizes the correlation between numeric variables. Warmer colors indicate a stronger positive correlation."

        elif chart_type == 'Histogram':
            x_col = chart_config.get('x')
            if not x_col:
                return "Variable must be selected for histogram."
            return f"This histogram shows the frequency distribution of '{x_col}', revealing the shape and spread of the data."

        elif chart_type == 'Gantt Chart':
            return "This Gantt chart displays the timeline and duration of different tasks or activities."

        elif chart_type == 'Gauge Chart':
            value = chart_config.get('value', 0)
            threshold = chart_config.get('threshold', 80)
            if isinstance(value, str) and value in df.columns:
                current_value = df[value].iloc[0] if len(df) > 0 else 0
            else:
                current_value = value

            performance = "above" if current_value > threshold else "below"
            return f"The gauge shows a current value of {current_value:.1f}, which is {performance} the threshold of {threshold}."

        elif chart_type == 'Waterfall Chart':
            return "This waterfall chart shows the cumulative effect of sequentially introduced positive or negative values."

        else:
            return "This chart visualizes the distribution and relationship of the selected data."

    except Exception:
        return "An automated narrative for this chart could not be generated."

def generate_story_suggestion(charts: list) -> str:
    """
    Analyzes the list of charts and suggests a narrative flow.
    Args:
        charts: A list of chart configuration dictionaries.
    Returns:
        A formatted markdown string with the suggested story.
    """
    if not charts:
        return "Add some charts to get a story suggestion."

    # Define a hierarchy for storytelling
    story_order = {
        'KPI & Composition': ['Donut Chart', 'Pie Chart', 'Treemap', 'Sunburst Chart', 'Funnel Chart', 'Gauge Chart'],
        'Trends & Time': ['Line Chart', 'Area Chart', 'Waterfall Chart'],
        'Comparisons & Rankings': ['Bar Chart', 'Gantt Chart'],
        'Relationships & Correlations': ['Scatter Plot', '3D Scatter Plot', 'Bubble Chart', 'Heatmap'],
        'Distributions': ['Box Plot', 'Violin Chart', 'Histogram'],
        'Data Tables': ['Data Table']
    }

    # Categorize existing charts
    categorized_charts = {
        'KPI & Composition': [],
        'Trends & Time': [],
        'Comparisons & Rankings': [],
        'Relationships & Correlations': [],
        'Distributions': [],
        'Data Tables': []
    }

    for chart in charts:
        chart_type = chart.get('type')
        chart_title = chart.get('title', 'Untitled')

        for category, types in story_order.items():
            if chart_type in types:
                categorized_charts[category].append(chart_title)
                break

    # Build the narrative string
    narrative = [
        "**💡 Suggested Narrative Flow**",
        "For a powerful presentation, I recommend organizing your charts to tell this story:"
    ]

    story_steps = []
    if categorized_charts['KPI & Composition']:
        story_steps.append(f"**Start with the big picture:** Lead with your KPI Cards and composition charts like *{', '.join(categorized_charts['KPI & Composition'])}* to give a high-level overview.")

    if categorized_charts['Trends & Time']:
        story_steps.append(f"**Show the trend:** Next, use your time-series charts like *{', '.join(categorized_charts['Trends & Time'])}* to show how performance has evolved.")

    if categorized_charts['Comparisons & Rankings']:
        story_steps.append(f"**Make comparisons:** Follow up with ranking charts like *{', '.join(categorized_charts['Comparisons & Rankings'])}* to highlight high and low performers.")

    if categorized_charts['Relationships & Correlations']:
        story_steps.append(f"**Explain the 'why':** Explore relationships between variables with charts like *{', '.join(categorized_charts['Relationships & Correlations'])}*.")

    if categorized_charts['Distributions']:
        story_steps.append(f"**Drill into details:** Analyze the spread of your data with distribution plots like *{', '.join(categorized_charts['Distributions'])}*.")

    if categorized_charts['Data Tables']:
        story_steps.append(f"**Provide the raw data:** Conclude with your data tables like *{', '.join(categorized_charts['Data Tables'])}* for reference.")

    if not story_steps:
        return "Could not generate a specific story. Try adding a variety of chart types."

    for i, step in enumerate(story_steps, 1):
        narrative.append(f"{i}. {step}")

    return "\n".join(narrative)
