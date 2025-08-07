import streamlit as st
import pandas as pd
import numpy as np

def render():
    """Renders the data type declaration page."""
    st.title("🔧 Declare Data Types")
    st.markdown("### Review and update the data types for each column in your dataset")

    if 'raw_df' not in st.session_state or st.session_state.raw_df is None:
        st.error("No data found. Please go back and upload a file.")
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = "upload"
            st.rerun()
        return

    df = st.session_state.raw_df

    # Display current data types
    st.subheader("Current Data Types")
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Column**")
        for col in df.columns:
            st.write(col)

    with col2:
        st.markdown("**Current Type**")
        for col in df.columns:
            st.write(str(df[col].dtype))

    st.divider()

    # Data type selection interface
    st.subheader("Update Column Data Types")
    st.markdown("Select the appropriate data type for each column:")

    # Available data types
    dtype_options = {
        'Keep Current': None,
        'Text/String': 'string',
        'Integer': 'int64',
        'Float': 'float64',
        'Boolean': 'bool',
        'Date/Time': 'datetime64[ns]',
        'Category': 'category'
    }

    # Store user selections
    if 'column_dtypes' not in st.session_state:
        st.session_state.column_dtypes = {}

    # Create form for data type selection
    with st.form("dtype_form"):
        cols = st.columns(2)

        for i, column in enumerate(df.columns):
            with cols[i % 2]:
                st.markdown(f"**{column}**")

                # Show sample values
                sample_values = df[column].dropna().head(5).tolist()
                st.caption(f"Sample values: {sample_values}")

                # Data type selector
                current_selection = st.session_state.column_dtypes.get(column, 'Keep Current')
                new_dtype = st.selectbox(
                    f"Data type for {column}",
                    options=list(dtype_options.keys()),
                    index=list(dtype_options.keys()).index(current_selection) if current_selection in dtype_options.keys() else 0,
                    key=f"dtype_{column}",
                    label_visibility="collapsed"
                )
                st.session_state.column_dtypes[column] = new_dtype

        # Submit button
        submitted = st.form_submit_button("✅ Apply Data Types", type="primary")

        if submitted:
            # Apply data type conversions
            updated_df = df.copy()
            conversion_log = []

            for column, dtype_selection in st.session_state.column_dtypes.items():
                if dtype_selection != 'Keep Current' and dtype_selection in dtype_options:
                    target_dtype = dtype_options[dtype_selection]

                    try:
                        if target_dtype == 'datetime64[ns]':
                            updated_df[column] = pd.to_datetime(updated_df[column], errors='coerce')
                        elif target_dtype == 'string':
                            updated_df[column] = updated_df[column].astype('string')
                        elif target_dtype == 'category':
                            updated_df[column] = updated_df[column].astype('category')
                        elif target_dtype in ['int64', 'float64', 'bool']:
                            if target_dtype == 'int64':
                                # Handle conversion to int more carefully
                                updated_df[column] = pd.to_numeric(updated_df[column], errors='coerce').fillna(0).astype(target_dtype)
                            else:
                                updated_df[column] = updated_df[column].astype(target_dtype)

                        conversion_log.append(f"✅ {column}: {df[column].dtype} → {target_dtype}")

                    except Exception as e:
                        conversion_log.append(f"❌ {column}: Failed to convert ({str(e)})")

            # Update the raw dataframe
            st.session_state.raw_df = updated_df

            # Show conversion results
            st.success("Data type conversions completed!")
            for log_entry in conversion_log:
                st.write(log_entry)

            # Auto-advance to next step
            st.session_state.step = "processing"
            st.rerun()

    # Preview updated dataframe
    st.subheader("Data Preview")
    preview_df = st.session_state.raw_df.head(10)
    st.dataframe(preview_df, use_container_width=True)

    # Navigation buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("⬅️ Back to Upload"):
            st.session_state.step = "upload"
            st.rerun()

    with col2:
        if st.button("Continue to Processing ➡️"):
            st.session_state.step = "processing"
            st.rerun()
