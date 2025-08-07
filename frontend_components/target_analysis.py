import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
import warnings
warnings.filterwarnings('ignore')

def calculate_mutual_information(df, target_variable):
    """Calculate mutual information scores for all features against target variable."""
    X = df.drop(columns=[target_variable])
    y = df[target_variable]

    # Prepare features - encode categorical variables
    X_processed = X.copy()
    label_encoders = {}

    for col in X_processed.select_dtypes(include=['object', 'category']).columns:
        le = LabelEncoder()
        X_processed[col] = le.fit_transform(X_processed[col].astype(str))
        label_encoders[col] = le

    # Fill missing values
    X_processed = X_processed.fillna(X_processed.mean())

    # Calculate mutual information
    if pd.api.types.is_numeric_dtype(y):
        # Regression case
        mi_scores = mutual_info_regression(X_processed, y, random_state=42)
        task_type = "regression"
    else:
        # Classification case  
        if not pd.api.types.is_numeric_dtype(y):
            le_target = LabelEncoder()
            y = le_target.fit_transform(y.astype(str))
        mi_scores = mutual_info_classif(X_processed, y, random_state=42)
        task_type = "classification"

    # Create results dataframe
    mi_df = pd.DataFrame({
        'Feature': X.columns,
        'Mutual_Information': mi_scores
    }).sort_values('Mutual_Information', ascending=False)

    return mi_df, task_type, X_processed, y

def calculate_feature_importance(X, y, task_type):
    """Calculate feature importance using Random Forest."""
    try:
        if task_type == "regression":
            rf = RandomForestRegressor(n_estimators=100, random_state=42)
        else:
            rf = RandomForestClassifier(n_estimators=100, random_state=42)

        rf.fit(X, y)

        importance_df = pd.DataFrame({
            'Feature': X.columns,
            'Importance': rf.feature_importances_
        }).sort_values('Importance', ascending=False)

        return importance_df
    except Exception as e:
        st.warning(f"Could not calculate Random Forest importance: {e}")
        return None

def render():
    """Renders the target variable analysis page with comprehensive reporting."""
    st.title("🎯 Target Variable Analysis")
    st.markdown("### Select a target variable and discover the most influential features")

    if 'processed_df' not in st.session_state or st.session_state.processed_df is None:
        st.error("No processed data found. Please complete the previous steps.")
        if st.button("⬅️ Back to Feature Engineering"):
            st.session_state.step = "manual_feature_creation"
            st.rerun()
        return

    df = st.session_state.processed_df

    # Step 1: Target Variable Selection
    st.subheader("Step 1: Select Target Variable")

    # Filter out columns that might not be good targets
    all_columns = df.columns.tolist()
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # Remove high-cardinality categorical columns from target options
    filtered_categorical = []
    for col in categorical_columns:
        if df[col].nunique() <= 20:  # Only include categorical columns with <= 20 unique values
            filtered_categorical.append(col)

    suitable_targets = numeric_columns + filtered_categorical

    if not suitable_targets:
        st.error("No suitable target variables found. All columns appear to be high-cardinality categorical variables.")
        return

    # FIXED: Improved target variable selection with better state management
    # Initialize session state for dropdown selections
    if 'selected_target_variable' not in st.session_state:
        st.session_state.selected_target_variable = "Select a target variable..."

    # Use a unique key and manage state properly
    target_variable = st.selectbox(
        "Choose your target variable:",
        options=["Select a target variable..."] + suitable_targets,
        index=0 if st.session_state.selected_target_variable == "Select a target variable..." or st.session_state.selected_target_variable not in suitable_targets 
        else suitable_targets.index(st.session_state.selected_target_variable) + 1,
        key="target_variable_selectbox"
    )

    # Update session state
    st.session_state.selected_target_variable = target_variable

    if target_variable == "Select a target variable...":
        st.info("👆 Please select a target variable to begin the analysis.")

        # Show variable information to help user choose
        st.subheader("📋 Available Variables")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Numeric Variables** (good for prediction)")
            for col in numeric_columns:
                unique_vals = df[col].nunique()
                col_range = f"Range: {df[col].min():.2f} - {df[col].max():.2f}" if pd.api.types.is_numeric_dtype(df[col]) else ""
                st.write(f"• **{col}**: {unique_vals} unique values {col_range}")

        with col2:
            st.markdown("**Categorical Variables** (good for classification)")
            for col in filtered_categorical:
                unique_vals = df[col].nunique()
                sample_vals = df[col].unique()[:3]
                st.write(f"• **{col}**: {unique_vals} categories (e.g., {list(sample_vals)})")

        # Navigation
        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("⬅️ Back to Feature Engineering"):
                st.session_state.step = "manual_feature_creation"
                st.rerun()

        with col2:
            if st.button("Skip to Clustering Analysis ➡️"):
                st.session_state.step = "clustering_analysis"
                st.rerun()

        return

    # Store selected target variable
    st.session_state.target_variable = target_variable

    # Display target variable information
    st.subheader("🔍 Target Variable Information")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Data Type", str(df[target_variable].dtype))
    with col2:
        st.metric("Unique Values", df[target_variable].nunique())
    with col3:
        missing_pct = (df[target_variable].isnull().sum() / len(df)) * 100
        st.metric("Missing Values", f"{missing_pct:.1f}%")
    with col4:
        if pd.api.types.is_numeric_dtype(df[target_variable]):
            st.metric("Mean Value", f"{df[target_variable].mean():.2f}")
        else:
            mode_val = df[target_variable].mode().iloc[0] if len(df[target_variable].mode()) > 0 else "N/A"
            st.metric("Most Common", str(mode_val))

    # Target variable distribution
    st.subheader("📊 Target Variable Distribution")

    if pd.api.types.is_numeric_dtype(df[target_variable]):
        # Numeric target - show histogram and box plot
        col1, col2 = st.columns(2)

        with col1:
            fig_hist = px.histogram(df, x=target_variable, 
                                  title=f"Distribution of {target_variable}",
                                  nbins=30)
            fig_hist.update_layout(template='plotly_dark', 
                                 paper_bgcolor='rgba(0,0,0,0)',
                                 plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_hist, use_container_width=True)

        with col2:
            fig_box = px.box(df, y=target_variable, 
                           title=f"Box Plot of {target_variable}")
            fig_box.update_layout(template='plotly_dark', 
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_box, use_container_width=True)

        # Summary statistics
        with st.expander("📈 Statistical Summary"):
            stats_df = df[target_variable].describe().to_frame(target_variable)
            st.dataframe(stats_df, use_container_width=True)

    else:
        # Categorical target - show value counts
        value_counts = df[target_variable].value_counts()

        fig_pie = px.pie(values=value_counts.values, names=value_counts.index,
                        title=f"Distribution of {target_variable}")
        fig_pie.update_layout(template='plotly_dark', 
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_pie, use_container_width=True)

    # Step 2: Feature Influence Analysis
    st.subheader("Step 2: 🔍 Feature Influence Analysis")

    # Check if analysis is already completed for this target
    analysis_key = f"analysis_{target_variable}"

    if st.button("🚀 Analyze Influential Variables", type="primary"):

        with st.spinner("Analyzing feature importance and relationships..."):

            # Calculate mutual information
            try:
                mi_df, task_type, X_processed, y_processed = calculate_mutual_information(df, target_variable)

                st.success(f"✅ Analysis completed! Task type: **{task_type.title()}**")

                # Store results in session state with target-specific key
                analysis_results = {
                    'target_variable': target_variable,
                    'task_type': task_type,
                    'mi_df': mi_df,
                    'X_processed': X_processed,
                    'y_processed': y_processed,
                    'completed': True
                }

                # Random Forest Feature Importance
                rf_importance = calculate_feature_importance(X_processed, y_processed, task_type)
                if rf_importance is not None:
                    analysis_results['rf_importance'] = rf_importance

                # Store in session state
                st.session_state[analysis_key] = analysis_results

                st.success("🎉 Target variable analysis completed! Results saved for the next steps.")

            except Exception as e:
                st.error(f"Error during analysis: {e}")
                st.info("Please try selecting a different target variable or check your data quality.")

    # Display analysis results if available
    if analysis_key in st.session_state and st.session_state[analysis_key].get('completed'):

        analysis_results = st.session_state[analysis_key]
        mi_df = analysis_results['mi_df']
        task_type = analysis_results['task_type']

        st.success(f"✅ Analysis completed! Task type: **{task_type.title()}**")

        # Display mutual information results
        st.subheader("📊 Mutual Information Analysis")
        st.markdown("*Mutual Information measures the dependency between features and the target variable*")

        # Top 10 features by mutual information
        top_mi = mi_df.head(10)

        if len(top_mi) > 0:
            # Create bar chart
            fig_mi = px.bar(top_mi, x='Mutual_Information', y='Feature',
                           orientation='h',
                           title='Top Features by Mutual Information',
                           labels={'Mutual_Information': 'Mutual Information Score'})
            fig_mi.update_layout(template='plotly_dark', 
                               paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(0,0,0,0)',
                               height=400)
            st.plotly_chart(fig_mi, use_container_width=True)

            # Show detailed table
            with st.expander("📋 Detailed Mutual Information Scores"):
                st.dataframe(mi_df, use_container_width=True)

        # Random Forest Feature Importance
        if 'rf_importance' in analysis_results:
            st.subheader("🌲 Random Forest Feature Importance")
            st.markdown("*Random Forest importance shows how much each feature contributes to prediction accuracy*")

            rf_importance = analysis_results['rf_importance']
            top_rf = rf_importance.head(10)

            # Create bar chart
            fig_rf = px.bar(top_rf, x='Importance', y='Feature',
                           orientation='h',
                           title='Top Features by Random Forest Importance',
                           labels={'Importance': 'Feature Importance'})
            fig_rf.update_layout(template='plotly_dark', 
                               paper_bgcolor='rgba(0,0,0,0)',
                               plot_bgcolor='rgba(0,0,0,0)',
                               height=400)
            st.plotly_chart(fig_rf, use_container_width=True)

            # Show detailed table
            with st.expander("📋 Detailed Random Forest Importance"):
                st.dataframe(rf_importance, use_container_width=True)

        # Feature Relationship Analysis - FIXED: Persistent dropdown selection
        st.subheader("🔗 Feature Relationships with Target")

        top_features = top_mi['Feature'].head(5).tolist()

        if len(top_features) > 0:
            # Initialize session state for feature selection
            feature_key = f"selected_feature_{target_variable}"
            if feature_key not in st.session_state:
                st.session_state[feature_key] = top_features[0]  # Default to first feature

            # FIXED: Persistent feature selection dropdown
            selected_feature = st.selectbox(
                "Select a feature to analyze its relationship with the target:",
                top_features,
                index=top_features.index(st.session_state[feature_key]) if st.session_state[feature_key] in top_features else 0,
                key=f"feature_relationship_selectbox_{target_variable}"
            )

            # Update session state
            st.session_state[feature_key] = selected_feature

            # Create relationship visualizations
            if pd.api.types.is_numeric_dtype(df[target_variable]) and pd.api.types.is_numeric_dtype(df[selected_feature]):
                # Both numeric - scatter plot
                fig_scatter = px.scatter(df, x=selected_feature, y=target_variable,
                                       title=f'Relationship: {selected_feature} vs {target_variable}',
                                       trendline="ols")
                fig_scatter.update_layout(template='plotly_dark', 
                                        paper_bgcolor='rgba(0,0,0,0)',
                                        plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_scatter, use_container_width=True)

                # Calculate correlation
                correlation = df[selected_feature].corr(df[target_variable])
                st.info(f"📈 Correlation coefficient: **{correlation:.3f}**")

            elif pd.api.types.is_numeric_dtype(df[target_variable]):
                # Numeric target, categorical feature - box plot
                fig_box = px.box(df, x=selected_feature, y=target_variable,
                               title=f'{target_variable} by {selected_feature}')
                fig_box.update_layout(template='plotly_dark', 
                                    paper_bgcolor='rgba(0,0,0,0)',
                                    plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_box, use_container_width=True)

            else:
                # Both categorical - stacked bar chart
                crosstab = pd.crosstab(df[selected_feature], df[target_variable])

                fig_stack = px.bar(crosstab, 
                                 title=f'Cross-tabulation: {selected_feature} vs {target_variable}')
                fig_stack.update_layout(template='plotly_dark', 
                                      paper_bgcolor='rgba(0,0,0,0)',
                                      plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_stack, use_container_width=True)

        # Key Insights Summary
        st.subheader("💡 Key Insights")

        insights = []

        if len(top_mi) > 0:
            top_feature = top_mi.iloc[0]
            insights.append(f"🏆 **Most influential feature**: {top_feature['Feature']} (MI Score: {top_feature['Mutual_Information']:.4f})")

        if task_type == "regression":
            insights.append(f"📊 **Analysis Type**: Regression (predicting numeric values)")
            insights.append(f"🎯 **Target Range**: {df[target_variable].min():.2f} to {df[target_variable].max():.2f}")
        else:
            insights.append(f"📊 **Analysis Type**: Classification (predicting categories)")
            insights.append(f"🎯 **Target Classes**: {df[target_variable].nunique()} different categories")

        high_influence_features = mi_df[mi_df['Mutual_Information'] > 0.1]
        insights.append(f"⭐ **High-influence features**: {len(high_influence_features)} features with MI > 0.1")

        if len(mi_df) > 0:
            avg_mi = mi_df['Mutual_Information'].mean()
            insights.append(f"📈 **Average MI Score**: {avg_mi:.4f}")

        for insight in insights:
            st.markdown(insight)

    # Navigation buttons
    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Back to Feature Engineering"):
            st.session_state.step = "manual_feature_creation"
            st.rerun()

    with col2:
        if st.button("Continue to Clustering Analysis ➡️"):
            st.session_state.step = "clustering_analysis"
            st.rerun()
