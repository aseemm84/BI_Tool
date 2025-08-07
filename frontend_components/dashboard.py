import streamlit as st
from backend import utils, narratives
from .charts import render_chart, render_dashboard_layout

def render_sidebar(df):
    """Renders the sidebar for dashboard controls."""
    with st.sidebar:
        st.header("🎛️ Dashboard Controls")

        if st.button("🔄 Reset Dashboard", use_container_width=True):
            st.session_state.charts = []
            st.session_state.kpi_cards = []
            st.session_state.story_suggestion = ""
            st.rerun()

        with st.expander("⚙️ Dashboard Settings", expanded=True):
            st.session_state.dashboard_settings['layout'] = st.selectbox(
                "Layout Resolution",
                options=['1366x768', '1440x900', '1920x1080 (Full HD)', '2560x1440 (QHD)', '3840x2160 (4K UHD)'],
                index=2
            )

        st.header("📊 KPI Cards")
        available_measures = list(st.session_state.get('available_measures', {}).keys())
        selected_kpis = st.multiselect(
            "Select up to 3 measures for KPI cards",
            options=available_measures,
            default=st.session_state.get('kpi_cards', []),
            max_selections=3
        )
        st.session_state.kpi_cards = selected_kpis

        # CORRECTED STORYTELLING ASSISTANT - ALWAYS VISIBLE
        st.header("📖 Storytelling Assistant")

        # Show suggestion button regardless of chart count
        if st.button("💡 Generate Story Suggestion", use_container_width=True):
            if len(st.session_state.charts) >= 1:
                st.session_state.story_suggestion = narratives.generate_story_suggestion(st.session_state.charts)
            else:
                st.session_state.story_suggestion = "Add some charts to get a meaningful story suggestion."

        # Display story suggestion if available
        if st.session_state.story_suggestion:
            st.markdown("**Story Suggestion:**")
            st.markdown(st.session_state.story_suggestion)

        # Chart arrangement (only show if charts exist)
        if len(st.session_state.charts) >= 2:
            with st.expander("📐 Arrange Dashboard", expanded=False):
                chart_titles = [c['title'] for c in st.session_state.charts]
                ordered_titles = st.multiselect(
                    "Reorder your charts:",
                    options=chart_titles,
                    default=chart_titles
                )

                if st.button("🔄 Update Layout", use_container_width=True):
                    if ordered_titles:
                        chart_map = {c['title']: c for c in st.session_state.charts}
                        st.session_state.charts = [chart_map[title] for title in ordered_titles if title in chart_map]
                        st.rerun()
        elif len(st.session_state.charts) == 1:
            st.info("Add more charts to enable reordering.")
        else:
            st.info("Add charts to enable storytelling features.")

        # CORRECTED EXPORT OPTIONS - NOW AVAILABLE
        st.header("📥 Export Options")

        # Export processed data
        if st.button("📊 Download Processed Data (Excel)", use_container_width=True):
            try:
                excel_data = utils.to_excel(df)
                st.download_button(
                    label="📥 Click to Download Excel File",
                    data=excel_data,
                    file_name="processed_data.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating Excel file: {e}")

        # Export dashboard as CSV
        if st.button("📋 Download Data as CSV", use_container_width=True):
            try:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Click to Download CSV File",
                    data=csv,
                    file_name="dashboard_data.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error creating CSV file: {e}")

        # Export charts configuration (JSON)
        if st.session_state.charts:
            if st.button("⚙️ Export Dashboard Config", use_container_width=True):
                import json
                config_data = {
                    'charts': st.session_state.charts,
                    'kpi_cards': st.session_state.kpi_cards,
                    'dashboard_settings': st.session_state.dashboard_settings
                }
                config_json = json.dumps(config_data, indent=2)
                st.download_button(
                    label="📥 Click to Download Dashboard Config",
                    data=config_json,
                    file_name="dashboard_config.json",
                    mime="application/json",
                    use_container_width=True
                )

        render_add_chart_form(df)

        st.sidebar.markdown("---")
        st.sidebar.markdown("""
        <div style="text-align: center;">
            <p>Created by <strong>Aseem Mehrotra</strong></p>
            <a href="https://linkedin.com/in/aseem-mehrotra" target="_blank">LinkedIn Profile</a>
        </div>
        """, unsafe_allow_html=True)

def render_add_chart_form(df):
    """Renders the form in the sidebar to add a new chart."""
    st.header("➕ Add a New Chart")

    if len(st.session_state.charts) >= 10:
        st.warning("Maximum of 10 charts reached.")
        return

    # ALL CHART TYPES INCLUDING MISSING ONES
    chart_types = [
        "Bar Chart", "Line Chart", "Scatter Plot", "3D Scatter Plot", "Donut Chart", "Data Table", 
        "Bubble Chart", "Box Plot", "Histogram", "Violin Chart", "Treemap", "Heatmap", 
        "Sunburst Chart", "Funnel Chart", "Gantt Chart", "Area Chart", "Pie Chart", 
        "Gauge Chart", "Waterfall Chart"
    ]

    chart_type = st.selectbox("Select Chart Type", sorted(chart_types), key="chart_type_selector")

    with st.form(key=f"chart_form_{chart_type}", clear_on_submit=True):
        st.subheader(f"Configure {chart_type}")

        chart_id = st.session_state.chart_id_counter
        chart_config = {'type': chart_type, 'id': f"chart_{chart_id}"}
        chart_config['title'] = st.text_input("Chart Title", value=f"New {chart_type}")

        compatible_cols = utils.get_chart_compatible_columns(df, chart_type)

        # Chart specific configuration inputs with CORRECTED COLOR SELECTION
        if chart_type in ["Bar Chart", "Line Chart", "Area Chart", "Histogram", "Box Plot", "Violin Chart"]:
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            # CORRECTED: Color selection now properly configured
            color_options = [None] + df.columns.tolist()
            chart_config['color'] = st.selectbox("Color by (optional)", color_options)

        elif chart_type == "Scatter Plot":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            # CORRECTED: Color selection now properly configured
            color_options = [None] + df.columns.tolist()
            chart_config['color'] = st.selectbox("Color by (optional)", color_options)

        elif chart_type == "3D Scatter Plot":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['z'] = st.selectbox("Z-axis", compatible_cols.get('z', []))
            # CORRECTED: Color selection now properly configured
            color_options = [None] + df.columns.tolist()
            chart_config['color'] = st.selectbox("Color by (optional)", color_options)

        elif chart_type == "Bubble Chart":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['size_col'] = st.selectbox("Size", compatible_cols.get('size', []))
            # CORRECTED: Color selection now properly configured
            chart_config['color'] = st.selectbox("Color", df.columns.tolist())

        elif chart_type == "Data Table":
            all_cols = compatible_cols.get('all', [])
            chart_config['columns'] = st.multiselect("Select columns", all_cols, default=all_cols[:5])

        elif chart_type in ["Donut Chart", "Pie Chart", "Funnel Chart"]:
            chart_config['names'] = st.selectbox("Categories", compatible_cols.get('names', []))
            chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))

        elif chart_type in ["Treemap", "Sunburst Chart"]:
            path_cols = compatible_cols.get('path', [])
            chart_config['path'] = st.multiselect("Hierarchy Path", path_cols, default=path_cols[:2] if len(path_cols) >= 2 else path_cols)
            chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))

        elif chart_type == "Gantt Chart":
            chart_config['Task'] = st.selectbox("Task Column", compatible_cols.get('Task', []))
            chart_config['Start'] = st.selectbox("Start Date Column", compatible_cols.get('Start', []))
            chart_config['Finish'] = st.selectbox("Finish Date Column", compatible_cols.get('Finish', []))

        elif chart_type == "Gauge Chart":
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            chart_config['value'] = st.selectbox("Value Column", numeric_cols)
            chart_config['max_value'] = st.number_input("Max Value", value=100)
            chart_config['threshold'] = st.number_input("Threshold", value=80)
            chart_config['reference'] = st.number_input("Reference Value", value=0)

        elif chart_type == "Waterfall Chart":
            chart_config['x'] = st.selectbox("Categories", compatible_cols.get('names', []))
            chart_config['y'] = st.selectbox("Values", compatible_cols.get('values', []))
            measure_options = ["relative", "total", "absolute"]
            chart_config['measure'] = st.selectbox("Measure Type", measure_options)

        if st.form_submit_button("➕ Add Chart to Dashboard"):
            st.session_state.charts.append(chart_config)
            st.session_state.chart_id_counter += 1
            st.rerun()

def render():
    """Renders the main dashboard page."""
    is_presentation_mode = st.query_params.get("present") == "true"
    df = st.session_state.processed_df

    if not is_presentation_mode:
        st.title("🎨 Your Interactive Dashboard")
        st.markdown("### Create stunning visualizations and insights from your data")

        if st.session_state.charts:
            if st.button("📽️ Present Dashboard", type="primary"):
                st.query_params["present"] = "true"
                st.rerun()

        render_sidebar(df)
    else:
        col1, col2 = st.columns([1, 6])
        with col1:
            if st.button("⬅️ Exit Presentation"):
                st.query_params.clear()
                st.rerun()
        with col2:
            st.title("📊 Dashboard Presentation")

    # --- Main dashboard area ---
    if st.session_state.kpi_cards:
        st.subheader("📊 Key Performance Indicators")
        kpi_cols = st.columns(len(st.session_state.kpi_cards))
        all_measures = st.session_state.get('available_measures', {})

        for i, kpi_name in enumerate(st.session_state.kpi_cards):
            with kpi_cols[i]:
                value = all_measures.get(kpi_name, 0)
                formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                st.metric(label=kpi_name, value=formatted_value)

        st.markdown("---")

    # Render charts
    render_dashboard_layout(st.session_state.charts, df)

    # Show helpful tips for empty dashboard
    if not st.session_state.charts and not is_presentation_mode:
        st.info("""
        🎯 **Get Started with Your Dashboard:**

        1. **Add KPI Cards** - Select key metrics from the sidebar
        2. **Create Charts** - Use the "Add a New Chart" form in the sidebar
        3. **Customize** - Adjust chart sizes and colors
        4. **Get Story Suggestions** - Use the Storytelling Assistant
        5. **Export Data** - Download your processed data in multiple formats
        6. **Present** - Click "Present Dashboard" for full-screen view
        """)
