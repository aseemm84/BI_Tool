import streamlit as st
from backend import engineering

def render():
    """Renders the segmentation choice page."""
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
