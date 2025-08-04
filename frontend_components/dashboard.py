import streamlit as st
from backend import utils, narratives
from .charts import render_chart, render_dashboard_layout

def render_sidebar(df):
    """Renders the sidebar for dashboard controls."""
    with st.sidebar:
        st.header("Dashboard Controls")
        if st.button("🔄 Reset Dashboard", use_container_width=True):
            st.session_state.charts = []
            st.session_state.kpi_cards = []
            st.session_state.story_suggestion = ""
            st.rerun()

        with st.expander("Dashboard Settings", expanded=True):
            st.session_state.dashboard_settings['layout'] = st.selectbox(
                "Layout Resolution",
                options=['1366x768', '1440x900', '1920x1080 (Full HD)', '2560x1440 (QHD)', '3840x2160 (4K UHD)'],
                index=2
            )

        st.header("KPI Cards")
        available_measures = list(st.session_state.get('available_measures', {}).keys())
        selected_kpis = st.multiselect(
            "Select up to 3 measures for KPI cards",
            options=available_measures,
            default=st.session_state.get('kpi_cards', []),
            max_selections=3
        )
        st.session_state.kpi_cards = selected_kpis

        st.header("Storytelling Assistant")
        if len(st.session_state.charts) >= 4:
            if st.button("💡 Suggest Story Order", use_container_width=True):
                st.session_state.story_suggestion = narratives.generate_story_suggestion(st.session_state.charts)

            if st.session_state.story_suggestion:
                st.markdown(st.session_state.story_suggestion)
                with st.expander("Arrange Your Dashboard", expanded=True):
                    chart_titles = [c['title'] for c in st.session_state.charts]
                    ordered_titles = st.multiselect(
                        "Select the order of your charts:",
                        options=chart_titles,
                        default=chart_titles
                    )
                    if st.button("Update Dashboard Layout", use_container_width=True):
                        chart_map = {c['title']: c for c in st.session_state.charts}
                        st.session_state.charts = [chart_map[title] for title in ordered_titles]
                        st.rerun()
        else:
            st.info("Add at least 4 charts to enable the Storytelling Assistant.")

        st.header("Export Options")
        st.download_button(
            label="📥 Download Processed Data (Excel)",
            data=utils.to_excel(df),
            file_name="processed_data.xlsx",
            mime="application/vnd.ms-excel",
            use_container_width=True
        )

        render_add_chart_form(df)

        st.sidebar.markdown("---")
        st.sidebar.markdown("""<div style="text-align: center; padding-top: 10px;"><p style="margin-bottom: 5px;">Created by Aseem Mehrotra</p><a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank" style="color: #ff0084;">LinkedIn Profile</a></div>""", unsafe_allow_html=True)


def render_add_chart_form(df):
    """Renders the form in the sidebar to add a new chart."""
    st.header("Add a New Chart")
    if len(st.session_state.charts) >= 10:
        st.warning("Maximum of 10 charts reached.")
        return

    chart_types = ["Bar Chart", "Line Chart", "Scatter Plot", "3D Scatter Plot", "Donut Chart", "Data Table", "Bubble Chart", "Box Plot", "Histogram", "Violin Chart", "Treemap", "Heatmap", "Sunburst Chart", "Funnel Chart", "Gantt Chart"]
    chart_type = st.selectbox("Select Chart Type", sorted(chart_types), key="chart_type_selector")

    with st.form(key=f"chart_form_{chart_type}", clear_on_submit=True):
        st.subheader(f"Configure {chart_type}")
        
        chart_id = st.session_state.chart_id_counter
        chart_config = {'type': chart_type, 'id': f"chart_{chart_id}"}
        chart_config['title'] = st.text_input("Chart Title", value=f"New {chart_type}")
        
        compatible_cols = utils.get_chart_compatible_columns(df, chart_type)

        # --- Chart specific configuration inputs ---
        if chart_type in ["Bar Chart", "Line Chart", "Histogram", "Box Plot", "Violin Chart"]:
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('x', []))
        elif chart_type == "Scatter Plot":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('color', []))
        elif chart_type == "3D Scatter Plot":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['z'] = st.selectbox("Z-axis", compatible_cols.get('z', []))
            chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('color', []))
        elif chart_type == "Bubble Chart":
            chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
            chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
            chart_config['size_col'] = st.selectbox("Size", compatible_cols.get('size', []))
            chart_config['color'] = st.selectbox("Color", compatible_cols.get('color', []))
        elif chart_type == "Data Table":
            all_cols = compatible_cols.get('all', [])
            chart_config['columns'] = st.multiselect("Select columns", all_cols, default=all_cols[:5])
        elif chart_type in ["Donut Chart", "Funnel Chart"]:
            chart_config['names'] = st.selectbox("Categories", compatible_cols.get('names', []))
            chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))
        elif chart_type in ["Treemap", "Sunburst Chart"]:
            path_cols = compatible_cols.get('path', [])
            chart_config['path'] = st.multiselect("Hierarchy Path", path_cols, default=path_cols[:2])
            chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))
        elif chart_type == "Gantt Chart":
            chart_config['Task'] = st.selectbox("Task Column", compatible_cols.get('Task', []))
            chart_config['Start'] = st.selectbox("Start Date Column", compatible_cols.get('Start', []))
            chart_config['Finish'] = st.selectbox("Finish Date Column", compatible_cols.get('Finish', []))

        if st.form_submit_button("Add Chart to Dashboard"):
            st.session_state.charts.append(chart_config)
            st.session_state.chart_id_counter += 1
            st.rerun()

def render():
    """Renders the main dashboard page."""
    is_presentation_mode = st.query_params.get("present") == "true"
    df = st.session_state.processed_df

    if not is_presentation_mode:
        st.title("🎨 Your Interactive Dashboard")
        if st.session_state.charts:
            if st.button("Present 📽️"):
                st.query_params["present"] = "true"
                st.rerun()
        render_sidebar(df)
    else:
        if st.button("⬅️ Exit Presentation"):
            st.query_params.clear()
            st.rerun()

    # --- Main dashboard area ---
    if st.session_state.kpi_cards:
        kpi_cols = st.columns(len(st.session_state.kpi_cards))
        all_measures = st.session_state.get('available_measures', {})
        for i, kpi_name in enumerate(st.session_state.kpi_cards):
            with kpi_cols[i]:
                value = all_measures.get(kpi_name, 0)
                formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                st.metric(label=kpi_name, value=formatted_value)
        st.markdown("---")

    render_dashboard_layout(st.session_state.charts, df)
