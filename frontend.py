import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64

from backend import cleaning, analysis, engineering, utils, narratives

# --- Helper Functions ---
def reset_app():
    """Clears all session state variables and reruns the app."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Page Configuration ---
st.set_page_config(page_title="BI Tool v1.0 by Aseem Mehrotra", page_icon="🚀", layout="wide")

# --- Session State Initialization ---
if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'processed_df' not in st.session_state: st.session_state.processed_df = None
if 'charts' not in st.session_state: st.session_state.charts = []
if 'theme' not in st.session_state: st.session_state.theme = "Light"
if 'processing_log' not in st.session_state: st.session_state.processing_log = {}

# --- Main App Logic ---
# Check if the app is in presentation mode from the query parameters
is_presentation_mode = st.query_params.get("present") == "true"

# Step 1: Welcome Screen
if st.session_state.step == "welcome":
    st.title("🚀 Welcome to the Advanced BI Tool (v1.0)")
    st.markdown("**Transform raw data into beautiful, insightful, and presentation-ready dashboards in minutes.**")
    if st.button("Let's Get Started!", type="primary"):
        st.session_state.step = "upload"
        st.rerun()

# Step 2: File Upload
elif st.session_state.step == "upload":
    st.title("1. Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file:
        try:
            st.session_state.raw_df = pd.read_csv(uploaded_file)
            st.session_state.step = "processing"
            st.rerun()
        except Exception as e: st.error(f"Error reading file: {e}")
    if st.button("⬅️ Back to Welcome"): reset_app()

# Step 3: Automated Processing
elif st.session_state.step == "processing":
    st.title("⚙️ Processing Your Data...")
    if 'raw_df' in st.session_state:
        with st.spinner("Cleaning data..."):
            cleaned_df, log1 = cleaning.clean_data(st.session_state.raw_df.copy())
        with st.spinner("Performing advanced analysis..."):
            _, log2 = analysis.run_full_analysis(cleaned_df)
        with st.spinner("Engineering new features..."):
            engineered_df, log3 = engineering.engineer_features_automated(cleaned_df)
        st.session_state.processing_log = {**log1, **log2, **log3}
        st.session_state.processed_df = engineered_df
        st.session_state.step = "profiling_report"
        st.balloons()
        st.rerun()

# Step 4: Profiling Report
elif st.session_state.step == "profiling_report":
    st.title("📊 Data Profiling Report")
    st.info("Here's a summary of the automated actions performed on your data.")
    log = st.session_state.processing_log
    cols = st.columns(4)
    cols[0].metric("Missing Values Filled", log.get('missing_values_filled', 0))
    cols[1].metric("Duplicate Rows Removed", log.get('duplicates_removed', 0))
    cols[2].metric("Potential Outliers", log.get('outliers_identified', 0))
    cols[3].metric("New Features Engineered", log.get('features_engineered', 0))
    st.subheader("Key Driver Analysis")
    numeric_cols = st.session_state.processed_df.select_dtypes(include=np.number).columns.tolist()
    target_variable = st.selectbox("Select Target Variable to Analyze", options=[None] + numeric_cols)
    if target_variable:
        drivers = analysis.find_key_drivers(st.session_state.processed_df, target_variable)
        if drivers is not None: st.dataframe(drivers.rename("Correlation Strength"))
    if st.button("Continue to Manual Feature Creation ➡️", type="primary"):
        st.session_state.step = "manual_feature_creation"
        st.rerun()

# Step 5: Manual Feature Creation
elif st.session_state.step == "manual_feature_creation":
    st.title("🛠️ Manual Feature Creation")
    st.write("Create your own features to add to the dataset.")
    
    df = st.session_state.processed_df
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    feature_type = st.selectbox("Select Feature Type", ["Arithmetic (2 columns)", "Unary Transformation (1 column)", "Categorical Counts"])

    with st.form("feature_form"):
        if feature_type == "Arithmetic (2 columns)":
            st.subheader("Arithmetic Operation")
            col1 = st.selectbox("Select first column", numeric_cols)
            col2 = st.selectbox("Select second column", numeric_cols)
            operation = st.selectbox("Select operation", ['add', 'subtract', 'multiply', 'divide'])
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'arithmetic', 'col1': col1, 'col2': col2, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {col1}_{operation}_{col2}")
        
        elif feature_type == "Unary Transformation (1 column)":
            st.subheader("Unary Transformation")
            col = st.selectbox("Select a numeric column", numeric_cols)
            operation = st.selectbox("Select operation", ['log', 'square', 'sqrt', 'average'])
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'unary', 'col': col, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {operation}_of_{col}")

        elif feature_type == "Categorical Counts":
            st.subheader("Categorical Counts")
            col = st.selectbox("Select a categorical column", categorical_cols)
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'categorical_count', 'col': col}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {col}_counts")

    st.dataframe(st.session_state.processed_df.head())
    if st.button("Continue to Segmentation ➡️", type="primary"):
        st.session_state.step = "segmentation_choice"
        st.rerun()

# Step 6: Segmentation Choice
elif st.session_state.step == "segmentation_choice":
    st.title("🔬 Automated Segmentation")
    n_clusters = st.slider("How many segments to find?", 2, 10, 4)
    c1, c2 = st.columns(2)
    if c1.button("Yes, Create Segments", type="primary"):
        with st.spinner("Performing segmentation..."):
            df, log = engineering.perform_segmentation(st.session_state.processed_df, n_clusters)
            st.session_state.processed_df = df
            st.session_state.processing_log.update(log)
        st.session_state.step = "dashboard"
        st.rerun()
    if c2.button("No, Skip to Dashboard"):
        st.session_state.step = "dashboard"
        st.rerun()

# Step 7: Dashboard
elif st.session_state.step == "dashboard":
    if not is_presentation_mode:
        st.title("🎨 Your Interactive Dashboard")
        if st.session_state.charts:
            if st.button("Present 📽️"):
                st.query_params["present"] = "true"
                st.rerun()
    else:
        if st.button("⬅️ Exit Presentation"):
            st.query_params.clear()
            st.rerun()

    df = st.session_state.processed_df
    if not is_presentation_mode:
        with st.sidebar:
            st.header("Dashboard Controls")
            st.session_state.theme = st.radio("Select Theme", ["Light", "Dark"])
            if st.button("🔄 Reset Dashboard", use_container_width=True): st.session_state.charts = []
            st.header("Export Options")
            st.download_button(label="📥 Download Processed Data (Excel)", data=utils.to_excel(df), file_name="processed_data.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
            st.header("Add a New Chart")
            if len(st.session_state.charts) >= 10:
                st.warning("Maximum of 10 charts reached.")
            else:
                chart_types = ["Bar Chart", "Line Chart", "Scatter Plot", "3D Scatter Plot", "Donut Chart", "Data Table", "Bubble Chart", "Box Plot", "Histogram", "Violin Chart", "Treemap", "Heatmap", "Sunburst Chart", "Funnel Chart", "Gantt Chart"]
                chart_type = st.selectbox("Select Chart Type", sorted(chart_types))
                with st.form(f"chart_form_{chart_type}"):
                    st.subheader(f"Configure {chart_type}")
                    chart_config = {'type': chart_type, 'id': f"chart_{len(st.session_state.charts)}"}
                    chart_config['title'] = st.text_input("Chart Title", value=f"New {chart_type}")
                    compatible_cols = utils.get_chart_compatible_columns(df, chart_type)
                    
                    if chart_type in ["Bar Chart", "Line Chart", "Histogram", "Box Plot", "Violin Chart"]:
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                    elif chart_type == "Scatter Plot":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                    elif chart_type == "3D Scatter Plot":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['z'] = st.selectbox("Z-axis", compatible_cols.get('z', []))
                    elif chart_type == "Bubble Chart":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['size'] = st.selectbox("Size", compatible_cols.get('size', []))
                        chart_config['color'] = st.selectbox("Color", compatible_cols.get('color', []))
                    elif chart_type == "Data Table":
                        all_cols = compatible_cols.get('all', [])
                        chart_config['columns'] = st.multiselect("Select columns to display", all_cols, default=all_cols[:5])
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
                        st.rerun()

            # Branding section
            st.sidebar.markdown("---")
            linkedin_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-linkedin"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>"""
            b64_linkedin_icon = base64.b64encode(linkedin_icon_svg.encode()).decode()
            st.sidebar.markdown(f"""<div style="text-align: center; padding-top: 10px;"><p style="margin-bottom: 5px;">Created by Aseem Mehrotra</p><a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank"><img src="data:image/svg+xml;base64,{b64_linkedin_icon}" alt="LinkedIn" width="24" height="24"></a></div>""", unsafe_allow_html=True)

    # Main dashboard area for displaying charts
    if not st.session_state.charts: 
        st.info("Your dashboard is empty. Add some charts from the sidebar!")
    else:
        for i, chart_config in enumerate(st.session_state.charts):
            with st.container(border=True):
                st.subheader(chart_config.get('title', 'Chart'))
                try:
                    plotly_template = 'plotly_white' if st.session_state.theme == "Light" else 'plotly_dark'
                    fig = None
                    narrative_text = ""

                    # Handle Data Table separately as it doesn't use Plotly
                    if chart_config['type'] == "Data Table":
                        st.dataframe(df[chart_config.get('columns', df.columns)], use_container_width=True)
                        narrative_text = f"Displaying {len(chart_config.get('columns', df.columns))} selected columns."
                    else:
                        # The rest of the charts use Plotly
                        if chart_config['type'] == "Heatmap":
                            corr = df[utils.get_chart_compatible_columns(df, 'Heatmap')['numeric_only']].corr()
                            fig = px.imshow(corr, text_auto=True, aspect="auto")
                        elif chart_config['type'] == "Gantt Chart":
                            fig = px.timeline(df, x_start=chart_config['Start'], x_end=chart_config['Finish'], y=chart_config['Task'])
                        elif chart_config['type'] == "Bar Chart": 
                            fig = px.bar(df, x=chart_config.get('x'), y=chart_config.get('y'))
                        elif chart_config['type'] == "Line Chart": 
                            fig = px.line(df, x=chart_config.get('x'), y=chart_config.get('y'))
                        elif chart_config['type'] == "Scatter Plot": 
                            fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'))
                        elif chart_config['type'] == "3D Scatter Plot": 
                            fig = px.scatter_3d(df, x=chart_config.get('x'), y=chart_config.get('y'), z=chart_config.get('z'))
                        elif chart_config['type'] == "Bubble Chart":
                             fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'), size=chart_config.get('size'), color=chart_config.get('color'))
                        elif chart_config['type'] == "Donut Chart": 
                            fig = px.pie(df, names=chart_config.get('names'), values=chart_config.get('values'), hole=0.5)
                        elif chart_config['type'] == "Funnel Chart":
                            fig = px.funnel(df, x=chart_config.get('names'), y=chart_config.get('values'))
                        elif chart_config['type'] == "Treemap": 
                            fig = px.treemap(df, path=chart_config.get('path'), values=chart_config.get('values'))
                        elif chart_config['type'] == "Sunburst Chart": 
                            fig = px.sunburst(df, path=chart_config.get('path'), values=chart_config.get('values'))
                        elif chart_config['type'] == "Violin Chart": 
                            fig = px.violin(df, x=chart_config.get('x'), y=chart_config.get('y'), box=True)
                        elif chart_config['type'] == "Box Plot":
                            fig = px.box(df, x=chart_config.get('x'), y=chart_config.get('y'))
                        elif chart_config['type'] == "Histogram":
                            fig = px.histogram(df, x=chart_config.get('x'), y=chart_config.get('y'))

                        if fig:
                            fig.update_layout(template=plotly_template, title_text="")
                            st.plotly_chart(fig, use_container_width=True)
                        
                        narrative_text = narratives.generate_narrative(chart_config, df)

                    st.markdown(f"**💡 Insight:** {narrative_text}")

                except Exception as e: 
                    st.error(f"Could not create chart '{chart_config.get('title')}': {e}")
                
                if not is_presentation_mode:
                    if st.button("🗑️ Remove", key=f"del_{chart_config['id']}", use_container_width=True):
                        st.session_state.charts = [c for c in st.session_state.charts if c['id'] != chart_config['id']]
                        st.rerun()
