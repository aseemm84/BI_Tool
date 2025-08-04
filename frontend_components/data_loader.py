import streamlit as st
import pandas as pd
import io
from .welcome import reset_app

def render_upload_page():
    """Renders the page for uploading data files."""
    st.title("1. Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            st.session_state.uploaded_file_data = uploaded_file.getvalue()
            file_name = uploaded_file.name

            if file_name.endswith('.csv'):
                st.session_state.raw_df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
                st.session_state.step = "processing"
                st.rerun()
            elif file_name.endswith('.xlsx'):
                excel_file = pd.ExcelFile(io.BytesIO(st.session_state.uploaded_file_data))
                st.session_state.sheet_names = excel_file.sheet_names

                if len(st.session_state.sheet_names) == 1:
                    st.session_state.raw_df = pd.read_excel(excel_file, sheet_name=st.session_state.sheet_names[0])
                    st.session_state.step = "processing"
                    st.rerun()
                else:
                    st.session_state.step = "select_sheet"
                    st.rerun()
        except Exception as e:
            st.error(f"Error reading file: {e}")

    if st.button("⬅️ Back to Welcome"):
        reset_app()

def render_sheet_selection_page():
    """Renders the page for selecting a sheet from an Excel file."""
    st.title("2. Select a Sheet")
    st.info("Your Excel file contains multiple sheets. Please select one to analyze.")

    selected_sheet = st.selectbox(
        "Available Sheets",
        options=st.session_state.sheet_names
    )

    if st.button("Load Sheet and Continue", type="primary"):
        try:
            excel_file = pd.ExcelFile(io.BytesIO(st.session_state.uploaded_file_data))
            st.session_state.raw_df = pd.read_excel(excel_file, sheet_name=selected_sheet)
            st.session_state.step = "processing"
            st.rerun()
        except Exception as e:
            st.error(f"Could not load sheet '{selected_sheet}': {e}")

    if st.button("⬅️ Back to Upload"):
        st.session_state.step = "upload"
        if 'sheet_names' in st.session_state: del st.session_state.sheet_names
        if 'uploaded_file_data' in st.session_state: del st.session_state.uploaded_file_data
        st.rerun()
