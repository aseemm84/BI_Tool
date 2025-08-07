import streamlit as st
from backend import cleaning, analysis, engineering

def render():
    """Renders the data processing spinner page."""
    st.title("⚙️ Processing Your Data...")
    st.markdown("### Automated data cleaning, analysis, and feature engineering in progress")

    if 'raw_df' in st.session_state and st.session_state.raw_df is not None:

        # Show processing steps
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Step 1: Data Cleaning
        status_text.text("Step 1/3: Cleaning data and removing useless columns...")
        progress_bar.progress(25)

        with st.spinner("Cleaning data and removing useless columns..."):
            cleaned_df, log1 = cleaning.clean_data(st.session_state.raw_df.copy())

        progress_bar.progress(50)
        status_text.text("Step 2/3: Performing advanced analysis...")

        with st.spinner("Performing advanced analysis..."):
            _, log2 = analysis.run_full_analysis(cleaned_df)

        progress_bar.progress(75)
        status_text.text("Step 3/3: Engineering new features and measures...")

        with st.spinner("Engineering new features and measures..."):
            engineered_df, log3 = engineering.engineer_features_automated(cleaned_df)

        progress_bar.progress(100)
        status_text.text("Processing completed successfully!")

        # Store results
        st.session_state.processing_log = {**log1, **log2, **log3}
        st.session_state.processed_df = engineered_df

        # Show completion summary
        st.success("🎉 Data processing completed successfully!")

        # Display processing summary
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Rows Processed", f"{len(engineered_df):,}")

        with col2:
            st.metric("Features Created", log3.get('features_engineered', 0))

        with col3:
            st.metric("Measures Generated", len(log3.get('measures', {})))

        st.balloons()

        # Auto-advance after a short delay
        import time
        time.sleep(2)
        st.session_state.step = "profiling_report"
        st.rerun()

    else:
        st.error("No data found to process. Please go back and upload a file.")
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = "upload"
            st.rerun()
