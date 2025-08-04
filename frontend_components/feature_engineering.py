import streamlit as st
from backend import engineering

def render():
    """Renders the manual feature creation page."""
    st.title("🛠️ Manual Feature Creation")
    st.write("Create your own features to add to the dataset.")

    df = st.session_state.processed_df
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
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
                st.rerun()

        elif feature_type == "Unary Transformation (1 column)":
            st.subheader("Unary Transformation")
            col = st.selectbox("Select a numeric column", numeric_cols)
            operation = st.selectbox("Select operation", ['log', 'square', 'sqrt', 'average'])
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'unary', 'col': col, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {operation}_of_{col}")
                st.rerun()

        elif feature_type == "Categorical Counts":
            st.subheader("Categorical Counts")
            col = st.selectbox("Select a categorical column", categorical_cols)
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'categorical_count', 'col': col}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {col}_counts")
                st.rerun()

    # Display a preview of the dataframe
    df_display = st.session_state.processed_df.head().copy()
    for col in df_display.select_dtypes(include='category').columns:
        df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display)

    if st.button("Continue to Segmentation ➡️", type="primary"):
        st.session_state.step = "segmentation_choice"
        st.rerun()
