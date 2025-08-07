import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from backend import engineering

def analyze_segments(df, segment_col='Segment'):
    """Analyze the created segments and generate insights."""
    if segment_col not in df.columns:
        return None

    analysis = {}

    # Basic segment statistics
    segment_counts = df[segment_col].value_counts().sort_index()
    analysis['segment_counts'] = segment_counts
    analysis['num_segments'] = len(segment_counts)

    # Segment size analysis
    total_rows = len(df)
    segment_percentages = (segment_counts / total_rows * 100).round(1)
    analysis['segment_percentages'] = segment_percentages

    # Largest and smallest segments
    analysis['largest_segment'] = segment_counts.idxmax()
    analysis['smallest_segment'] = segment_counts.idxmin()
    analysis['size_difference'] = segment_counts.max() - segment_counts.min()

    # Segment balance assessment
    expected_size = total_rows / len(segment_counts)
    max_deviation = abs(segment_counts - expected_size).max()
    analysis['balance_score'] = 1 - (max_deviation / expected_size)  # 1 = perfectly balanced, 0 = highly imbalanced

    # Analyze numeric features by segment
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    if segment_col in numeric_cols:
        numeric_cols.remove(segment_col)

    segment_profiles = {}
    if numeric_cols:
        for col in numeric_cols:
            segment_means = df.groupby(segment_col)[col].mean()
            segment_stds = df.groupby(segment_col)[col].std()
            segment_profiles[col] = {
                'means': segment_means,
                'stds': segment_stds,
                'range': segment_means.max() - segment_means.min()
            }

    analysis['segment_profiles'] = segment_profiles

    # Analyze categorical features by segment
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    categorical_profiles = {}

    for col in categorical_cols:
        segment_modes = df.groupby(segment_col)[col].agg(lambda x: x.mode().iloc[0] if len(x.mode()) > 0 else 'N/A')
        categorical_profiles[col] = segment_modes

    analysis['categorical_profiles'] = categorical_profiles

    return analysis

def render():
    """Renders the segmentation choice page with comprehensive reporting."""
    st.title("🎨 Data Segmentation")
    st.markdown("### Apply clustering to segment your data based on the analysis")

    # Check if clustering analysis was completed
    if 'clustering_results' not in st.session_state or not st.session_state.clustering_results:
        st.warning("⚠️ Clustering analysis not completed. Using default segmentation approach.")
        recommended_k = 4

        st.info("""
        **Note**: For optimal results, complete the clustering analysis first to get:
        - Data-driven recommendations for number of clusters
        - Quality metrics (Silhouette scores)
        - Visualizations of cluster separation
        """)
    else:
        clustering_results = st.session_state.clustering_results
        recommended_k = clustering_results['analysis_results'].get('final_recommended_k', 4)

        st.subheader("🎯 Clustering Analysis Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Recommended K", recommended_k)
        with col2:
            score = clustering_results['analysis_results'].get('silhouette_best_score', 0)
            st.metric("Best Silhouette Score", f"{score:.3f}")

        # Show brief summary
        st.info(f"✅ Analysis suggests **{recommended_k} clusters** provide the best balance of cohesion and separation.")

    # Check if segmentation has already been performed
    segments_created = 'Segment' in st.session_state.processed_df.columns if st.session_state.processed_df is not None else False

    if not segments_created:
        # Show segmentation configuration
        st.subheader("🔧 Segmentation Configuration")

        n_clusters = st.slider("Number of segments to create:", 2, 10, recommended_k)

        if n_clusters != recommended_k and 'clustering_results' in st.session_state:
            st.warning(f"You've selected {n_clusters} clusters, but analysis recommends {recommended_k}.")

        # Preview what will happen
        st.markdown(f"""
        **What will happen when you create segments:**
        - Apply K-Means clustering to group similar data points
        - Add a new 'Segment' column to your dataset  
        - Each row will be assigned to segment 0, 1, 2, ... {n_clusters-1}
        - You can then analyze differences between segments in your dashboard
        """)

        # Action buttons
        col1, col2 = st.columns(2)

        if col1.button("✅ Create Segments", type="primary"):
            with st.spinner("Performing segmentation..."):
                df, log = engineering.perform_segmentation(st.session_state.processed_df, n_clusters)
                st.session_state.processed_df = df
                st.session_state.processing_log.update(log)

                st.success(f"🎉 Successfully created {n_clusters} segments!")

                # Store segmentation results and rerun to show report
                if 'Segment' in df.columns:
                    analysis = analyze_segments(df)
                    st.session_state.segmentation_analysis = analysis

                # FIXED: Remove automatic redirect, let user see the report
                st.rerun()

        if col2.button("⏭️ Skip to Dashboard"):
            st.session_state.step = "dashboard"
            st.rerun()

        # Show current data info
        st.subheader("📋 Current Dataset Info")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Rows", len(st.session_state.processed_df))
        with col2:
            st.metric("Total Columns", len(st.session_state.processed_df.columns))
        with col3:
            numeric_cols = st.session_state.processed_df.select_dtypes(include=np.number).columns
            st.metric("Numeric Columns", len(numeric_cols))

    else:
        # FIXED: Show segmentation report with manual navigation
        st.success("🎉 Segmentation completed! Here's your comprehensive analysis:")

        df = st.session_state.processed_df

        # Display the comprehensive segmentation report
        if 'segmentation_analysis' in st.session_state:
            analysis = st.session_state.segmentation_analysis
        else:
            # Generate analysis if not already stored
            analysis = analyze_segments(df)
            st.session_state.segmentation_analysis = analysis

        if analysis:
            st.header("📊 Comprehensive Segmentation Report")

            # 1. Segment Overview
            st.subheader("🔍 Segment Overview")

            segment_counts = analysis['segment_counts']
            segment_percentages = analysis['segment_percentages']

            # Create segment distribution chart
            fig_dist = px.pie(
                values=segment_counts.values,
                names=[f"Segment {i}" for i in segment_counts.index],
                title="Segment Size Distribution"
            )
            fig_dist.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_dist, use_container_width=True)

            # Create columns for segment metrics
            segment_cols = st.columns(min(len(segment_counts), 4))

            for i, (segment, count) in enumerate(segment_counts.items()):
                col_idx = i % len(segment_cols)
                with segment_cols[col_idx]:
                    percentage = segment_percentages[segment]
                    st.metric(f"Segment {segment}", f"{count:,} rows", f"{percentage}%")

            # 2. Segment Balance Analysis
            st.subheader("⚖️ Segment Balance Analysis")

            balance_score = analysis['balance_score']

            if balance_score > 0.8:
                balance_status = "🟢 Well Balanced"
                balance_desc = "Segments are relatively equal in size."
            elif balance_score > 0.6:
                balance_status = "🟡 Moderately Balanced"
                balance_desc = "Some size differences between segments."
            else:
                balance_status = "🔴 Imbalanced"
                balance_desc = "Significant size differences between segments."

            col1, col2 = st.columns([1, 3])
            with col1:
                st.metric("Balance Score", f"{balance_score:.2f}")
            with col2:
                st.write(f"**Status**: {balance_status}")
                st.write(balance_desc)
                st.write(f"• Largest segment: Segment {analysis['largest_segment']} ({segment_counts[analysis['largest_segment']]:,} rows)")
                st.write(f"• Smallest segment: Segment {analysis['smallest_segment']} ({segment_counts[analysis['smallest_segment']]:,} rows)")

            # 3. Numeric Features Analysis by Segment
            if analysis['segment_profiles']:
                st.subheader("📈 Numeric Features by Segment")

                # Select top features to display
                segment_profiles = analysis['segment_profiles']

                # Create comparison charts for top features
                top_features = sorted(segment_profiles.keys(), 
                                    key=lambda x: segment_profiles[x]['range'], 
                                    reverse=True)[:4]  # Top 4 most variable features

                if len(top_features) >= 2:
                    cols = st.columns(2)
                    for i, feature in enumerate(top_features):
                        col_idx = i % 2
                        with cols[col_idx]:
                            means = segment_profiles[feature]['means']

                            fig_bar = px.bar(
                                x=[f"Segment {seg}" for seg in means.index],
                                y=means.values,
                                title=f"Average {feature} by Segment",
                                labels={'y': f'Average {feature}', 'x': 'Segment'}
                            )
                            fig_bar.update_layout(
                                template='plotly_dark',
                                paper_bgcolor='rgba(0,0,0,0)',
                                plot_bgcolor='rgba(0,0,0,0)',
                                height=350
                            )
                            st.plotly_chart(fig_bar, use_container_width=True)

                # Detailed feature comparison table
                with st.expander("📋 Detailed Numeric Feature Comparison"):
                    comparison_data = []
                    for feature, profile in segment_profiles.items():
                        for segment, mean_val in profile['means'].items():
                            std_val = profile['stds'][segment]
                            comparison_data.append({
                                'Feature': feature,
                                'Segment': f"Segment {segment}",
                                'Mean': round(mean_val, 3),
                                'Std Dev': round(std_val, 3)
                            })

                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True)

            # 4. Categorical Features Analysis by Segment
            if analysis['categorical_profiles']:
                st.subheader("🏷️ Categorical Features by Segment")

                categorical_profiles = analysis['categorical_profiles']

                # Create a summary table
                cat_summary = []
                for feature, segment_modes in categorical_profiles.items():
                    for segment, mode_val in segment_modes.items():
                        cat_summary.append({
                            'Feature': feature,
                            'Segment': f"Segment {segment}",
                            'Most Common Value': str(mode_val)
                        })

                if cat_summary:
                    cat_df = pd.DataFrame(cat_summary)
                    st.dataframe(cat_df, use_container_width=True)

            # 5. Key Insights and Recommendations
            st.subheader("💡 Key Insights & Recommendations")

            insights = []

            # Balance insights
            if balance_score > 0.8:
                insights.append("✅ **Well-balanced segmentation**: All segments have similar sizes, which is ideal for most analysis purposes.")
            elif balance_score < 0.5:
                insights.append("⚠️ **Imbalanced segmentation**: Consider adjusting the number of clusters or investigating outliers.")

            # Size insights
            total_rows = len(df)
            if segment_counts.max() > total_rows * 0.6:
                insights.append("📊 **Dominant segment detected**: One segment contains most of your data. Consider increasing the number of clusters.")
            elif segment_counts.min() < total_rows * 0.05:
                insights.append("🔍 **Small segment detected**: One segment is very small and might represent outliers or a niche group.")

            # Feature variation insights
            if analysis['segment_profiles']:
                high_variation_features = [f for f, p in segment_profiles.items() if p['range'] > segment_profiles[f]['means'].mean()]
                if high_variation_features:
                    insights.append(f"📈 **High variation features**: {', '.join(high_variation_features[:3])} show significant differences between segments.")

            # Usage recommendations
            insights.append("🎯 **Next steps**: Use these segments in your dashboard to:")
            insights.append("   • Compare KPIs across different customer groups")
            insights.append("   • Identify segment-specific trends and patterns")
            insights.append("   • Create targeted strategies for each segment")

            for insight in insights:
                st.markdown(insight)

            # 6. Sample Data by Segment
            st.subheader("👀 Sample Data by Segment")

            # Show a few examples from each segment
            for segment in sorted(df['Segment'].unique()):
                with st.expander(f"Sample data from Segment {segment}"):
                    segment_data = df[df['Segment'] == segment].head(3)
                    # Show only first 8 columns to avoid clutter
                    display_cols = df.columns.tolist()[:8]
                    if 'Segment' not in display_cols:
                        display_cols = ['Segment'] + display_cols[:7]
                    st.dataframe(segment_data[display_cols], use_container_width=True)

        # FIXED: Manual navigation with clear button
        st.divider()
        st.subheader("🚀 Ready to Build Your Dashboard?")
        st.markdown("""
        **You've successfully created segments!** Now you can:
        - Build interactive dashboards with segment-based analysis
        - Create charts that compare segments
        - Set up KPIs to track segment performance
        - Use the storytelling assistant to organize your insights
        """)

        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Back to Clustering"):
                # Allow user to go back and re-do clustering if needed
                st.session_state.step = "clustering_analysis"
                st.rerun()

        with col2:
            # FIXED: This is the main button users should click
            if st.button("🎨 Proceed to Dashboard Creation", type="primary", use_container_width=True):
                st.session_state.step = "dashboard"
                st.rerun()

        with col3:
            if st.button("🔄 Re-do Segmentation"):
                # Remove segment column to allow re-segmentation
                if 'Segment' in st.session_state.processed_df.columns:
                    st.session_state.processed_df = st.session_state.processed_df.drop('Segment', axis=1)
                if 'segmentation_analysis' in st.session_state:
                    del st.session_state.segmentation_analysis
                st.rerun()

    # Navigation (only show if segments not created yet)
    if not segments_created:
        st.divider()
        col1, col2 = st.columns([1, 1])

        with col1:
            if st.button("⬅️ Back to Clustering Analysis"):
                st.session_state.step = "clustering_analysis"
                st.rerun()

        with col2:
            if st.button("Continue to Dashboard ➡️"):
                st.session_state.step = "dashboard"
                st.rerun()
