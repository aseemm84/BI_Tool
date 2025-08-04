import streamlit as st
from backend import analysis

def render():
    """Renders the data profiling report page."""
    st.title("📊 Data Profiling Report")
    st.info("Here's a summary of the automated actions performed on your data.")
    log = st.session_state.processing_log

    # Display log metrics
    cols = st.columns(4)
    cols[0].metric("Missing Values Filled", log.get('missing_values_filled', 0))
    cols[1].metric("Duplicate Rows Removed", log.get('duplicates_removed', 0))
    cols[2].metric("Potential Outliers", log.get('outliers_identified', 0))
    cols[3].metric("New Features Engineered", log.get('features_engineered', 0))

    if log.get('useless_columns_removed'):
        st.warning(f"Removed useless columns: {', '.join(log['useless_columns_removed'])}")

    # Display Automated Measures
    if 'measures' in log and log['measures']:
        st.subheader("Automated Measures")
        st.session_state.available_measures = log['measures']
        measures = log['measures']
        num_measures = len(measures)
        num_cols = min(num_measures, 4)
        if num_cols > 0:
            measure_cols = st.columns(num_cols)
            for i, (name, value) in enumerate(measures.items()):
                col_index = i % num_cols
                formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                measure_cols[col_index].metric(label=name, value=formatted_value)

    st.subheader("Key Driver Analysis")
    numeric_cols = st.session_state.processed_df.select_dtypes(include='number').columns.tolist()
    target_variable = st.selectbox("Select Target Variable to Analyze", options=[None] + numeric_cols)
    if target_variable:
        drivers = analysis.find_key_drivers(st.session_state.processed_df, target_variable)
        if drivers is not None:
            st.dataframe(drivers.rename("Correlation Strength"))

    if st.button("Continue to Manual Feature Creation ➡️", type="primary"):
        st.session_state.step = "manual_feature_creation"
        st.rerun()
