import streamlit as st
from backend import engineering

def render():
    """Renders the manual feature creation page."""
    st.title("🛠️ Manual Feature Creation")
    st.markdown("### Create custom features to enhance your analysis")

    df = st.session_state.processed_df
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Feature creation interface
    feature_type = st.selectbox(
        "Select Feature Type", 
        ["Arithmetic (2 columns)", "Unary Transformation (1 column)", "Categorical Counts"]
    )

    with st.form("feature_form"):
        if feature_type == "Arithmetic (2 columns)":
            st.subheader("➕ Arithmetic Operation")
            col1 = st.selectbox("Select first column", numeric_cols, key="arith_col1")
            col2 = st.selectbox("Select second column", numeric_cols, key="arith_col2")
            operation = st.selectbox("Select operation", ['add', 'subtract', 'multiply', 'divide'])

            submitted = st.form_submit_button("Create Feature", type="primary")

            if submitted and col1 and col2:
                feature_def = {'type': 'arithmetic', 'col1': col1, 'col2': col2, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"✅ Created feature: {col1}_{operation}_{col2}")
                st.rerun()

        elif feature_type == "Unary Transformation (1 column)":
            st.subheader("🔄 Unary Transformation")
            col = st.selectbox("Select a numeric column", numeric_cols, key="unary_col")
            operation = st.selectbox("Select operation", ['log', 'square', 'sqrt', 'average'])

            submitted = st.form_submit_button("Create Feature", type="primary")

            if submitted and col:
                feature_def = {'type': 'unary', 'col': col, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"✅ Created feature: {operation}_of_{col}")
                st.rerun()

        elif feature_type == "Categorical Counts":
            st.subheader("📊 Categorical Counts")
            col = st.selectbox("Select a categorical column", categorical_cols, key="cat_col")

            submitted = st.form_submit_button("Create Feature", type="primary")

            if submitted and col:
                feature_def = {'type': 'categorical_count', 'col': col}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"✅ Created feature: {col}_counts")
                st.rerun()

    # Current dataset preview
    st.subheader("📋 Current Dataset")
    st.dataframe(st.session_state.processed_df.head(), use_container_width=True)

    # Navigation buttons
    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Back to Profiling Report"):
            st.session_state.step = "profiling_report"
            st.rerun()

    with col2:
        if st.button("Continue to Target Analysis ➡️", type="primary"):
            st.session_state.step = "target_analysis"
            st.rerun()
