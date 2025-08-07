import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
from backend import utils, narratives

def get_category_colors(chart_config: dict, df: pd.DataFrame) -> dict:
    """Manages color customization for categorical charts."""
    color_col = None

    if chart_config['type'] in ["Bar Chart", "Line Chart"] and 'color' in chart_config:
        color_col = chart_config.get('color')
    elif chart_config['type'] in ["Donut Chart", "Funnel Chart", "Treemap", "Sunburst Chart"]:
        color_col = chart_config.get('names') or (chart_config.get('path') and chart_config.get('path')[0])

    # ISSUE 4 FIX: Improved color customization functionality
    if color_col and df[color_col].dtype in ['object', 'category']:
        if 'colors' not in chart_config:
            chart_config['colors'] = {}

        unique_categories = df[color_col].unique()
        default_colors = px.colors.qualitative.Plotly

        with st.expander("🎨 Customize Colors"):
            color_changed = False
            for i, category in enumerate(unique_categories):
                key_safe_category = re.sub(r'[^A-Za-z0-9]+', '', str(category))
                color_key = f"color_{chart_config['id']}_{key_safe_category}"

                if category not in chart_config['colors']:
                    chart_config['colors'][category] = default_colors[i % len(default_colors)]

                # Store previous color to detect changes
                previous_color = chart_config['colors'][category]

                new_color = st.color_picker(
                    f"Color for {category}", 
                    value=chart_config['colors'][category], 
                    key=color_key
                )

                # Update color and mark change
                if new_color != previous_color:
                    chart_config['colors'][category] = new_color
                    color_changed = True

            # Force rerun if colors changed to update the chart
            if color_changed:
                st.rerun()

        return chart_config['colors']
    return None

def render_chart(chart_config: dict, df: pd.DataFrame):
    """Renders a single chart container with its controls."""
    is_presentation_mode = st.query_params.get("present") == "true"

    with st.container(border=True):
        st.subheader(chart_config.get('title', 'Chart'))

        try:
            plotly_template = 'plotly_dark'
            fig = None
            narrative_text = ""

            color_map = get_category_colors(chart_config, df)

            if chart_config['type'] == "Data Table":
                table_df = df[chart_config.get('columns', df.columns)].copy()
                for col in table_df.select_dtypes(include='category').columns:
                    table_df[col] = table_df[col].astype(str)
                st.dataframe(table_df, use_container_width=True)
                narrative_text = f"Displaying {len(chart_config.get('columns', df.columns))} selected columns."

            else:
                kwargs = {'color_discrete_map': color_map} if color_map else {}
                if 'color' in chart_config and chart_config['color']:
                    kwargs['color'] = chart_config['color']

                if chart_config['type'] == "Heatmap":
                    corr = df[utils.get_chart_compatible_columns(df, 'Heatmap')['numeric_only']].corr()
                    fig = px.imshow(corr, text_auto=True, aspect="auto", title="Correlation Heatmap")

                elif chart_config['type'] == "Gantt Chart":
                    fig = px.timeline(df, x_start=chart_config['Start'], x_end=chart_config['Finish'], y=chart_config['Task'], **kwargs)

                elif chart_config['type'] == "Bar Chart":
                    fig = px.bar(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                elif chart_config['type'] == "Line Chart":
                    fig = px.line(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                elif chart_config['type'] == "Scatter Plot":
                    fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                elif chart_config['type'] == "3D Scatter Plot":
                    fig = px.scatter_3d(df, x=chart_config.get('x'), y=chart_config.get('y'), z=chart_config.get('z'), **kwargs)

                elif chart_config['type'] == "Bubble Chart":
                    fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'), size=chart_config.get('size_col'), color=chart_config.get('color'))

                elif chart_config['type'] == "Donut Chart":
                    fig = px.pie(df, names=chart_config.get('names'), values=chart_config.get('values'), hole=0.5, **kwargs)

                elif chart_config['type'] == "Funnel Chart":
                    fig = px.funnel(df, x=chart_config.get('values'), y=chart_config.get('names'), **kwargs)

                elif chart_config['type'] == "Treemap":
                    fig = px.treemap(df, path=chart_config.get('path'), values=chart_config.get('values'), **kwargs)

                elif chart_config['type'] == "Sunburst Chart":
                    fig = px.sunburst(df, path=chart_config.get('path'), values=chart_config.get('values'), **kwargs)

                elif chart_config['type'] == "Violin Chart":
                    fig = px.violin(df, x=chart_config.get('x'), y=chart_config.get('y'), box=True, **kwargs)

                elif chart_config['type'] == "Box Plot":
                    fig = px.box(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                elif chart_config['type'] == "Histogram":
                    fig = px.histogram(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                # NEW CHART TYPES - PREVIOUSLY MISSING
                elif chart_config['type'] == "Area Chart":
                    fig = px.area(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                elif chart_config['type'] == "Pie Chart":
                    fig = px.pie(df, names=chart_config.get('names'), values=chart_config.get('values'), **kwargs)

                elif chart_config['type'] == "Gauge Chart":
                    # Gauge chart implementation
                    value = chart_config.get('value', 0)
                    if isinstance(value, str) and value in df.columns:
                        value = df[value].iloc[0] if len(df) > 0 else 0

                    fig = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = value,
                        domain = {'x': [0, 1], 'y': [0, 1]},
                        title = {'text': chart_config.get('title', 'Gauge')},
                        delta = {'reference': chart_config.get('reference', 0)},
                        gauge = {
                            'axis': {'range': [None, chart_config.get('max_value', 100)]},
                            'bar': {'color': "darkblue"},
                            'steps': [
                                {'range': [0, chart_config.get('max_value', 100) * 0.5], 'color': "lightgray"},
                                {'range': [chart_config.get('max_value', 100) * 0.5, chart_config.get('max_value', 100) * 0.8], 'color': "gray"}
                            ],
                            'threshold': {
                                'line': {'color': "red", 'width': 4},
                                'thickness': 0.75,
                                'value': chart_config.get('threshold', 90)
                            }
                        }
                    ))

                elif chart_config['type'] == "Waterfall Chart":
                    # ISSUE 3 FIX: Waterfall chart measure property fix
                    x_values = df[chart_config.get('x')].tolist() if chart_config.get('x') else []
                    y_values = df[chart_config.get('y')].tolist() if chart_config.get('y') else []

                    # Create measure array based on the selected measure type
                    measure_type = chart_config.get('measure', 'relative')

                    if isinstance(measure_type, str):
                        # If measure_type is a single string, create an array
                        if measure_type == 'relative':
                            # All relative except potentially the last one
                            measure_array = ['relative'] * len(y_values)
                        elif measure_type == 'total':
                            # Set last as total, others as relative
                            measure_array = ['relative'] * (len(y_values) - 1) + ['total']
                        else:
                            # Default to relative
                            measure_array = ['relative'] * len(y_values)
                    else:
                        # Use the provided array directly
                        measure_array = measure_type

                    # Ensure measure array matches data length
                    if len(measure_array) != len(y_values) and y_values:
                        measure_array = ['relative'] * len(y_values)

                    fig = go.Figure(go.Waterfall(
                        name = "Waterfall",
                        orientation = "v",
                        measure = measure_array,  # Now properly an array
                        x = x_values,
                        textposition = "outside",
                        text = [f"{val:.1f}" if isinstance(val, (int, float)) else str(val) for val in y_values],
                        y = y_values,
                        connector = {"line":{"color":"rgb(63, 63, 63)"}},
                    ))

                # Set figure layout
                if fig:
                    fig.update_layout(
                        template=plotly_template, 
                        title_text="", 
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)', 
                        font_color="white",
                        xaxis=dict(gridcolor='rgba(255, 255, 255, 0.3)', linecolor='white', title_font_color="white", tickfont_color="white"),
                        yaxis=dict(gridcolor='rgba(255, 255, 255, 0.3)', linecolor='white', title_font_color="white", tickfont_color="white"),
                        legend_font_color="white", 
                        legend_title_font_color="white"
                    )
                    st.plotly_chart(fig, use_container_width=True)

                narrative_text = narratives.generate_narrative(chart_config, df)

            st.markdown(f"**💡 Insight:** {narrative_text}")

        except Exception as e:
            st.error(f"Could not create chart '{chart_config.get('title')}': {e}")

        if not is_presentation_mode:
            c1, c2 = st.columns([3, 1])
            chart_config['size'] = c1.slider("Chart Size (%)", 10, 100, chart_config.get('size', 50), key=f"size_{chart_config['id']}")
            if c2.button("🗑️ Remove", key=f"del_{chart_config['id']}", use_container_width=True):
                st.session_state.charts = [c for c in st.session_state.charts if c['id'] != chart_config['id']]
                st.rerun()

def render_dashboard_layout(charts: list, df: pd.DataFrame):
    """Renders the charts in a dynamic grid layout."""
    if not charts:
        st.info("Your dashboard is empty. Add some charts from the sidebar!")
        return

    row_buffer = []
    current_width = 0
    MAX_WIDTH = 100

    for chart_config in charts:
        chart_size = chart_config.get('size', 50)

        if current_width + chart_size > MAX_WIDTH:
            cols = st.columns([c.get('size', 50) for c in row_buffer])
            for j, c_config in enumerate(row_buffer):
                with cols[j]:
                    render_chart(c_config, df)

            row_buffer = [chart_config]
            current_width = chart_size
        else:
            row_buffer.append(chart_config)
            current_width += chart_size

    if row_buffer:
        cols = st.columns([c.get('size', 50) for c in row_buffer])
        for j, c_config in enumerate(row_buffer):
            with cols[j]:
                render_chart(c_config, df)
