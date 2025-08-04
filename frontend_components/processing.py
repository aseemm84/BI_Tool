import streamlit as st
from backend import cleaning, analysis, engineering

def render():
    """Renders the data processing spinner page."""
    st.title("⚙️ Processing Your Data...")
    if 'raw_df' in st.session_state and st.session_state.raw_df is not None:
        with st.spinner("Cleaning data and removing useless columns..."):
            cleaned_df, log1 = cleaning.clean_data(st.session_state.raw_df.copy())
        with st.spinner("Performing advanced analysis..."):
            _, log2 = analysis.run_full_analysis(cleaned_df)
        with st.spinner("Engineering new features and measures..."):
            engineered_df, log3 = engineering.engineer_features_automated(cleaned_df)

        st.session_state.processing_log = {**log1, **log2, **log3}
        st.session_state.processed_df = engineered_df
        st.session_state.step = "profiling_report"
        st.balloons()
        st.rerun()
    else:
        st.error("No data found to process. Please go back and upload a file.")
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = "upload"
            st.rerun()
