import streamlit as st
import pandas as pd
import io
from backend import cleaning, analysis, engineering
from frontend_components import (
    welcome, data_loader, data_types, processing, profiling,
    feature_engineering, target_analysis, clustering_analysis, segmentation, dashboard
)

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Advanced Business Intelligence Tool", page_icon="🚀", layout="wide")

# Apply custom CSS for the app theme with corrected sidebar text color
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.1);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    .chart-container {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(5px);
        margin-bottom: 1rem;
    }
    .sidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(10px);
    }
    h1, h2, h3 {
        color: white !important;
    }
    .stSelectbox label, .stSlider label, .stMultiSelect label {
        color: white !important;
    }
    .stMarkdown p {
        color: white !important;
    }
    /* Sidebar text styling - make text black */
    .css-1d391kg, .css-1ht1j8u, .css-10trblm {
        color: black !important;
    }
    section[data-testid="stSidebar"] * {
        color: black !important;
    }
    section[data-testid="stSidebar"] .stMarkdown {
        color: black !important;
    }
    section[data-testid="stSidebar"] h1, 
    section[data-testid="stSidebar"] h2, 
    section[data-testid="stSidebar"] h3, 
    section[data-testid="stSidebar"] h4 {
        color: black !important;
    }
    section[data-testid="stSidebar"] label {
        color: black !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stSlider label, 
    section[data-testid="stSidebar"] .stMultiSelect label,
    section[data-testid="stSidebar"] .stTextInput label,
    section[data-testid="stSidebar"] .stButton label {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initializes all required session state variables."""
    if 'step' not in st.session_state: st.session_state.step = "welcome"
    if 'processed_df' not in st.session_state: st.session_state.processed_df = None
    if 'charts' not in st.session_state: st.session_state.charts = []
    if 'kpi_cards' not in st.session_state: st.session_state.kpi_cards = []
    if 'processing_log' not in st.session_state: st.session_state.processing_log = {}
    if 'story_suggestion' not in st.session_state: st.session_state.story_suggestion = ""
    if 'chart_id_counter' not in st.session_state: st.session_state.chart_id_counter = 0
    if 'dashboard_settings' not in st.session_state:
        st.session_state.dashboard_settings = {'layout': '1920x1080 (Full HD)'}
    if 'uploaded_file_data' not in st.session_state: st.session_state.uploaded_file_data = None
    if 'sheet_names' not in st.session_state: st.session_state.sheet_names = None
    if 'raw_df' not in st.session_state: st.session_state.raw_df = None
    if 'available_measures' not in st.session_state: st.session_state.available_measures = {}
    if 'column_dtypes' not in st.session_state: st.session_state.column_dtypes = {}
    if 'target_variable' not in st.session_state: st.session_state.target_variable = None
    if 'influential_analysis' not in st.session_state: st.session_state.influential_analysis = {}
    if 'clustering_results' not in st.session_state: st.session_state.clustering_results = {}

def main():
    """Main function to run the Streamlit app."""
    initialize_session_state()

    # --- Router to display the correct page based on the current step ---
    step = st.session_state.get('step', 'welcome')

    if step == "welcome":
        welcome.render()
    elif step == "upload":
        data_loader.render_upload_page()
    elif step == "select_sheet":
        data_loader.render_sheet_selection_page()
    elif step == "data_types":
        data_types.render()
    elif step == "processing":
        processing.render()
    elif step == "profiling_report":
        profiling.render()
    elif step == "manual_feature_creation":
        feature_engineering.render()
    elif step == "target_analysis":
        target_analysis.render()
    elif step == "clustering_analysis":
        clustering_analysis.render()
    elif step == "segmentation_choice":
        segmentation.render()
    elif step == "dashboard":
        dashboard.render()
    else:
        st.error("An unknown error occurred. Resetting the application.")
        welcome.reset_app()

if __name__ == "__main__":
    main()
