import streamlit as st
import pandas as pd
import numpy as np # Import numpy
import plotly.express as px
import base64

# Our modular backend is now even more powerful with a narratives module.
from backend import cleaning, analysis, engineering, utils, narratives

# --- Helper Functions ---
def reset_app():
    """Resets the session state to the beginning."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# --- Page Configuration ---
st.set_page_config(
    page_title="BI Tool v1.0 by Aseem Mehrotra",
    page_icon="🚀",
    layout="wide"
)

# --- Session State Initialization ---
if 'step' not in st.session_state:
    st.session_state.step = "welcome"
if 'processed_df' not in st.session_state:
    st.session_state.processed_df = None
if 'charts' not in st.session_state:
    st.session_state.charts = []
if 'theme' not in st.session_state:
    st.session_state.theme = "Light"
if 'processing_log' not in st.session_state:
    st.session_state.processing_log = {}

# --- Main App Logic ---
is_presentation_mode = "present" in st.query_params

# Step 1: Welcome Screen
if st.session_state.step == "welcome":
    st.title("🚀 Welcome to the Advanced BI Tool (v1.0)")
    st.markdown("""
    **Transform raw data into beautiful, insightful, and presentation-ready dashboards in minutes.**
    
    This tool automates the entire analytics workflow. This is the first official version, ready for you to explore.
    """)
    if st.button("Let's Get Started!", type="primary"):
        st.session_state.step = "upload"
        st.rerun()

# Step 2: File Upload
elif st.session_state.step == "upload":
    st.title("1. Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    if uploaded_file is not None:
        try:
            st.session_state.raw_df = pd.read_csv(uploaded_file)
            st.session_state.step = "processing"
            st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")
    if st.button("⬅️ Back to Welcome"):
        reset_app()

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
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Missing Values Filled", log.get('missing_values_filled', 0))
    col2.metric("Duplicate Rows Removed", log.get('duplicates_removed', 0))
    col3.metric("Potential Outliers", log.get('outliers_identified', 0))
    col4.metric("New Features Engineered", log.get('features_engineered', 0))

    st.subheader("Key Driver Analysis")
    st.write("Select a target variable to see which features influence it the most.")
    # FIX: Use np.number instead of pd.np.number
    numeric_cols = st.session_state.processed_df.select_dtypes(include=np.number).columns.tolist()
    target_variable = st.selectbox("Select Target Variable", options=[None] + numeric_cols)

    if target_variable:
        drivers = analysis.find_key_drivers(st.session_state.processed_df, target_variable)
        if drivers is not None:
            st.dataframe(drivers.rename("Correlation Strength"))

    if st.button("Continue to Segmentation ➡️", type="primary"):
        st.session_state.step = "segmentation_choice"
        st.rerun()

# Step 5: Segmentation Choice
elif st.session_state.step == "segmentation_choice":
    st.title("🔬 Automated Segmentation")
    st.write("Would you like to automatically segment your data into distinct groups using K-Means clustering? This can reveal hidden patterns.")
    n_clusters = st.slider("How many segments to find?", 2, 10, 4)

    c1, c2 = st.columns(2)
    if c1.button("Yes, Create Segments", type="primary"):
        with st.spinner("Performing segmentation..."):
            df, log = engineering.perform_segmentation(st.session_state.processed_df, n_clusters)
            st.session_state.processed_df = df
            st.session_state.processing_log.update(log)
            st.success(f"Successfully created {n_clusters} segments.")
        st.session_state.step = "dashboard"
        st.rerun()

    if c2.button("No, Skip to Dashboard"):
        st.session_state.step = "dashboard"
        st.rerun()

# Step 6: Dashboard
elif st.session_state.step == "dashboard":
    if not is_presentation_mode:
        st.title("🎨 Your Interactive Dashboard")
        if st.session_state.charts:
            st.link_button("Present 📽️", "?present=true")
    else:
        st.link_button("⬅️ Exit Presentation", "?")

    df = st.session_state.processed_df

    if not is_presentation_mode:
        with st.sidebar:
            st.header("Dashboard Controls")
            st.session_state.theme = st.radio("Select Theme", ["Light", "Dark"])
            if st.button("🔄 Reset Dashboard", use_container_width=True):
                st.session_state.charts = []
                st.rerun()
            st.header("Export Options")
            st.download_button(
                label="📥 Download Processed Data (Excel)",
                data=utils.to_excel(df),
                file_name="processed_data.xlsx",
                mime="application/vnd.ms-excel",
                use_container_width=True
            )
            st.header("Add a New Chart")
            if len(st.session_state.charts) >= 10:
                st.warning("Maximum of 10 charts reached.")
            else:
                chart_type = st.selectbox("Select Chart Type", ["Bar Chart", "Line Chart", "Scatter Plot", "Donut Chart", "Data Table"])
                with st.form("chart_form"):
                    st.subheader(f"Configure {chart_type}")
                    chart_config = {'type': chart_type, 'id': f"chart_{len(st.session_state.charts)}"}
                    chart_config['title'] = st.text_input("Chart Title", value=f"New {chart_type}")
                    compatible_cols = utils.get_chart_compatible_columns(df, chart_type)
                    if chart_type in ["Bar Chart", "Line Chart"]:
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                    elif chart_type == "Scatter Plot":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['color'] = st.selectbox("Color by", [None] + compatible_cols.get('color', []))
                    elif chart_type == "Donut Chart":
                        chart_config['names'] = st.selectbox("Categories", compatible_cols.get('names', []))
                        chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))
                    elif chart_type == "Data Table":
                        chart_config['columns'] = st.multiselect("Select columns", df.columns.tolist(), default=df.columns.tolist()[:5])
                    if st.form_submit_button("Add Chart to Dashboard"):
                        st.session_state.charts.append(chart_config)
                        st.rerun()
            st.sidebar.markdown("---")
            linkedin_icon_svg = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-linkedin"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>"""
            b64_linkedin_icon = base64.b64encode(linkedin_icon_svg.encode()).decode()
            st.sidebar.markdown(f"""<div style="text-align: center; padding-top: 10px;"><p style="margin-bottom: 5px;">Created by Aseem Mehrotra</p><a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank"><img src="data:image/svg+xml;base64,{b64_linkedin_icon}" alt="LinkedIn" width="24" height="24"></a></div>""", unsafe_allow_html=True)

    if not st.session_state.charts:
        st.info("Your dashboard is empty. Add some charts from the sidebar!")
    else:
        for i, chart_config in enumerate(st.session_state.charts):
            with st.container(border=True):
                st.subheader(chart_config.get('title', 'Chart'))
                try:
                    plotly_template = 'plotly_white' if st.session_state.theme == "Light" else 'plotly_dark'
                    fig = None
                    if chart_config['type'] == "Data Table":
                        st.dataframe(df[chart_config['columns']].style.background_gradient(cmap='viridis'))
                    else:
                        if chart_config['type'] == "Bar Chart":
                            fig = px.bar(df, x=chart_config['x'], y=chart_config['y'])
                        elif chart_config['type'] == "Line Chart":
                            fig = px.line(df, x=chart_config['x'], y=chart_config['y'])
                        elif chart_config['type'] == "Scatter Plot":
                            fig = px.scatter(df, x=chart_config['x'], y=chart_config['y'], color=chart_config.get('color'))
                        elif chart_config['type'] == "Donut Chart":
                            fig = px.pie(df, names=chart_config['names'], values=chart_config['values'], hole=0.5)
                        if fig:
                            fig.update_layout(template=plotly_template, title_text="")
                            st.plotly_chart(fig, use_container_width=True)
                    narrative_text = narratives.generate_narrative(chart_config, df)
                    st.markdown(f"**💡 Insight:** {narrative_text}")
                except Exception as e:
                    st.error(f"Could not create chart: {e}")
                if not is_presentation_mode:
                    _, btn_col = st.columns([0.85, 0.15])
                    if btn_col.button("🗑️ Remove", key=f"del_{chart_config['id']}", use_container_width=True):
                        st.session_state.charts = [c for c in st.session_state.charts if c['id'] != chart_config['id']]
                        st.rerun()
