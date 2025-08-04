import streamlit as st
import pandas as pd
import io

from backend import cleaning, analysis, engineering
from frontend_components import (
    welcome, data_loader, processing, profiling,
    feature_engineering, segmentation, dashboard
)

# --- Page Configuration and Styling ---
st.set_page_config(page_title="Advanced Business Intelligence Tool", page_icon="🚀", layout="wide")

# Apply custom CSS for the app theme
# This CSS is the same as in your original file.
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%);
        color: white;
    }
    /* Main content area styling */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 2rem;
        backdrop-filter: blur(10px);
    }
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    /* Button styling */
    .stButton>button, [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #ff0084, #f44336);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
    }
    .stButton>button:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #ff0084;
    }
    /* General text color */
    body, p, label, h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    /* Sidebar text color */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: white !important;
    }
    /* Container and expander styling */
    [data-testid="stVerticalBlock"], [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    /* Metric card styling */
    [data-testid="stMetric"] {
         background-color: rgba(255, 255, 255, 0.1);
         border-radius: 10px;
         padding: 1rem;
    }
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        border-color: rgba(255, 255, 255, 0.3);
    }
    /* Selectbox dropdown readability */
    .st-emotion-cache-1jicfl2 {
        background-color: #4a00e0;
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
    elif step == "processing":
        processing.render()
    elif step == "profiling_report":
        profiling.render()
    elif step == "manual_feature_creation":
        feature_engineering.render()
    elif step == "segmentation_choice":
        segmentation.render()
    elif step == "dashboard":
        dashboard.render()
    else:
        st.error("An unknown error occurred. Resetting the application.")
        welcome.reset_app()

if __name__ == "__main__":
    main()
