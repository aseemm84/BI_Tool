import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend import analysis

def render():
    """Renders the data profiling report page with visual charts."""
    st.title("📊 Data Profiling Report")
    st.markdown("### Comprehensive analysis of your processed data with visual insights")

    log = st.session_state.processing_log
    df = st.session_state.processed_df

    # Display processing metrics
    st.subheader("🔧 Processing Summary") 
    cols = st.columns(4)
    cols[0].metric("Missing Values Filled", log.get('missing_values_filled', 0))
    cols[1].metric("Duplicate Rows Removed", log.get('duplicates_removed', 0))
    cols[2].metric("Potential Outliers", log.get('outliers_identified', 0))
    cols[3].metric("New Features Engineered", log.get('features_engineered', 0))

    if log.get('useless_columns_removed'):
        st.warning(f"🗑️ Removed useless columns: {', '.join(log['useless_columns_removed'])}")

    # Display Automated Measures
    if 'measures' in log and log['measures']:
        st.subheader("📈 Automated Measures")
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

    # NEW: Visual Data Quality Charts
    st.subheader("📊 Data Quality Visualizations")

    # 1. Missing Data Visualization
    missing_data = df.isnull().sum()
    if missing_data.sum() > 0:
        st.markdown("**Missing Data by Column**")
        missing_df = missing_data[missing_data > 0].reset_index()
        missing_df.columns = ['Column', 'Missing_Count']
        missing_df['Missing_Percentage'] = (missing_df['Missing_Count'] / len(df)) * 100

        fig_missing = px.bar(missing_df, x='Column', y='Missing_Count', 
                           title='Missing Values by Column',
                           labels={'Missing_Count': 'Number of Missing Values'})
        fig_missing.update_layout(template='plotly_dark', 
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_missing, use_container_width=True)
    else:
        st.success("✅ No missing data detected!")

    # 2. Data Types Distribution - FIXED JSON SERIALIZATION ERROR
    st.markdown("**Data Types Distribution**")

    # Convert data types to string to avoid JSON serialization issues
    dtype_counts = df.dtypes.astype(str).value_counts().reset_index()
    dtype_counts.columns = ['Data_Type', 'Count']

    # Clean up data type names for better display
    dtype_counts['Data_Type'] = dtype_counts['Data_Type'].replace({
        'object': 'Text/Object',
        'int64': 'Integer', 
        'Int64': 'Integer',
        'float64': 'Float',
        'Float64': 'Float',
        'bool': 'Boolean',
        'datetime64[ns]': 'DateTime',
        'category': 'Category',
        'string': 'String'
    })

    # Ensure Count column is numeric
    dtype_counts['Count'] = dtype_counts['Count'].astype(int)

    fig_dtypes = px.pie(dtype_counts, values='Count', names='Data_Type',
                       title='Distribution of Data Types')
    fig_dtypes.update_layout(template='plotly_dark', 
                           paper_bgcolor='rgba(0,0,0,0)',
                           plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_dtypes, use_container_width=True)

    # 3. Numeric Variables Distribution
    numeric_cols = df.select_dtypes(include='number').columns.tolist()
    if len(numeric_cols) > 0:
        st.markdown("**Numeric Variables Distribution**")

        # Create histograms for numeric columns
        if len(numeric_cols) <= 4:
            cols = st.columns(len(numeric_cols))
            for i, col in enumerate(numeric_cols):
                with cols[i]:
                    try:
                        fig_hist = px.histogram(df, x=col, title=f'Distribution of {col}')
                        fig_hist.update_layout(template='plotly_dark', 
                                             paper_bgcolor='rgba(0,0,0,0)',
                                             plot_bgcolor='rgba(0,0,0,0)',
                                             height=300)
                        st.plotly_chart(fig_hist, use_container_width=True)
                    except Exception as e:
                        st.error(f"Could not create histogram for {col}: {str(e)}")
        else:
            # For many numeric columns, show a selection
            selected_numeric = st.multiselect(
                "Select numeric columns to visualize:",
                numeric_cols,
                default=numeric_cols[:4]
            )

            if selected_numeric:
                cols = st.columns(min(len(selected_numeric), 2))
                for i, col in enumerate(selected_numeric):
                    with cols[i % 2]:
                        try:
                            fig_hist = px.histogram(df, x=col, title=f'Distribution of {col}')
                            fig_hist.update_layout(template='plotly_dark', 
                                                 paper_bgcolor='rgba(0,0,0,0)',
                                                 plot_bgcolor='rgba(0,0,0,0)',
                                                 height=300)
                            st.plotly_chart(fig_hist, use_container_width=True)
                        except Exception as e:
                            st.error(f"Could not create histogram for {col}: {str(e)}")

    # 4. Correlation Heatmap for Numeric Variables
    if len(numeric_cols) > 1:
        st.markdown("**Correlation Matrix**")
        try:
            corr_matrix = df[numeric_cols].corr()

            fig_corr = px.imshow(corr_matrix, 
                               text_auto=True, 
                               aspect="auto",
                               title="Correlation Matrix of Numeric Variables")
            fig_corr.update_layout(template='plotly_dark', 
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_corr, use_container_width=True)
        except Exception as e:
            st.error(f"Could not create correlation matrix: {str(e)}")

    # 5. Categorical Variables Analysis
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    if len(categorical_cols) > 0:
        st.markdown("**Categorical Variables Analysis**")

        # Show value counts for categorical columns
        if len(categorical_cols) <= 3:
            cols = st.columns(len(categorical_cols))
            for i, col in enumerate(categorical_cols):
                with cols[i]:
                    try:
                        if df[col].nunique() <= 10:  # Only show if not too many categories
                            value_counts = df[col].value_counts().head(10)
                            fig_cat = px.bar(x=value_counts.index, y=value_counts.values,
                                           title=f'Top Values in {col}')
                            fig_cat.update_layout(template='plotly_dark', 
                                                paper_bgcolor='rgba(0,0,0,0)',
                                                plot_bgcolor='rgba(0,0,0,0)',
                                                height=300)
                            st.plotly_chart(fig_cat, use_container_width=True)
                        else:
                            st.write(f"**{col}**: {df[col].nunique()} unique values (too many to display)")
                    except Exception as e:
                        st.error(f"Could not analyze categorical column {col}: {str(e)}")
        else:
            # For many categorical columns, show a selection
            selected_categorical = st.selectbox(
                "Select a categorical column to analyze:",
                categorical_cols
            )

            if selected_categorical and df[selected_categorical].nunique() <= 20:
                try:
                    value_counts = df[selected_categorical].value_counts().head(15)
                    fig_cat = px.bar(x=value_counts.index, y=value_counts.values,
                                   title=f'Value Distribution in {selected_categorical}')
                    fig_cat.update_layout(template='plotly_dark', 
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_cat, use_container_width=True)
                except Exception as e:
                    st.error(f"Could not create chart for {selected_categorical}: {str(e)}")

    # Data Quality Summary Table
    st.subheader("📋 Data Quality Summary")

    try:
        quality_data = []
        for col in df.columns:
            col_data = {
                'Column': col,
                'Data Type': str(df[col].dtype),
                'Non-Null Count': int(df[col].count()),
                'Null Count': int(df[col].isnull().sum()),
                'Null %': f"{(df[col].isnull().sum() / len(df)) * 100:.1f}%",
                'Unique Values': int(df[col].nunique()),
                'Duplicate %': f"{((len(df) - df[col].nunique()) / len(df)) * 100:.1f}%"
            }

            if df[col].dtype in ['int64', 'float64', 'Int64', 'Float64']:
                col_data['Min'] = float(df[col].min()) if pd.notna(df[col].min()) else 'N/A'
                col_data['Max'] = float(df[col].max()) if pd.notna(df[col].max()) else 'N/A'
                col_data['Mean'] = f"{float(df[col].mean()):.2f}" if pd.notna(df[col].mean()) else 'N/A'
            else:
                col_data['Min'] = 'N/A'
                col_data['Max'] = 'N/A'
                col_data['Mean'] = 'N/A'

            quality_data.append(col_data)

        quality_df = pd.DataFrame(quality_data)
        st.dataframe(quality_df, use_container_width=True)
    except Exception as e:
        st.error(f"Could not create quality summary table: {str(e)}")

    # Key Driver Analysis Preview
    st.subheader("🔍 Key Driver Analysis Preview")
    numeric_cols = df.select_dtypes(include='number').columns.tolist()

    if len(numeric_cols) > 1:
        target_variable = st.selectbox(
            "Select a variable to explore correlations:", 
            options=["Select a variable..."] + numeric_cols
        )

        if target_variable != "Select a variable...":
            try:
                drivers = analysis.find_key_drivers(df, target_variable)
                if drivers is not None and len(drivers) > 0:
                    st.markdown(f"**Top correlations with {target_variable}:**")

                    # Create a bar chart of correlations
                    correlation_df = drivers.to_frame("Correlation_Strength").reset_index()
                    correlation_df.columns = ["Feature", "Correlation_Strength"]

                    fig_drivers = px.bar(correlation_df, x='Feature', y='Correlation_Strength',
                                       title=f'Key Drivers for {target_variable}')
                    fig_drivers.update_layout(template='plotly_dark', 
                                            paper_bgcolor='rgba(0,0,0,0)',
                                            plot_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(fig_drivers, use_container_width=True)

                    # Also show the table
                    st.dataframe(correlation_df, use_container_width=True)
                else:
                    st.info("No significant correlations found.")
            except Exception as e:
                st.error(f"Could not perform key driver analysis: {str(e)}")
    else:
        st.info("Add more numeric variables through feature engineering to enable correlation analysis.")

    # Sample data preview
    st.subheader("👀 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    # Summary Statistics
    if len(numeric_cols) > 0:
        with st.expander("📈 Statistical Summary"):
            try:
                st.dataframe(df[numeric_cols].describe(), use_container_width=True)
            except Exception as e:
                st.error(f"Could not create statistical summary: {str(e)}")

    # Next steps information
    st.subheader("🎯 Next Steps")
    st.info("""
    **What's Next:**
    1. **Manual Feature Creation**: Add domain-specific features to enhance your analysis
    2. **Target Variable Selection**: Choose what you want to predict or analyze  
    3. **Clustering Analysis**: Discover hidden patterns in your data
    4. **Dashboard Creation**: Build interactive visualizations
    """)

    # Navigation
    if st.button("Continue to Manual Feature Creation ➡️", type="primary"):
        st.session_state.step = "manual_feature_creation"
        st.rerun()
