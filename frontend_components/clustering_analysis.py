import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, silhouette_samples
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import matplotlib.cm as cm

def calculate_wcss(X, max_clusters=10):
    """Calculate Within-Cluster Sum of Squares for elbow method."""
    wcss = []
    k_range = range(1, max_clusters + 1)

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        kmeans.fit(X)
        wcss.append(kmeans.inertia_)

    return k_range, wcss

def calculate_silhouette_scores(X, max_clusters=10):
    """Calculate silhouette scores for different number of clusters."""
    silhouette_scores = []
    k_range = range(2, max_clusters + 1)  # Silhouette score needs at least 2 clusters

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(X)
        silhouette_avg = silhouette_score(X, cluster_labels)
        silhouette_scores.append(silhouette_avg)

    return k_range, silhouette_scores

def create_silhouette_plot(X, n_clusters):
    """Create detailed silhouette analysis plot."""
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    cluster_labels = kmeans.fit_predict(X)

    silhouette_avg = silhouette_score(X, cluster_labels)
    sample_silhouette_values = silhouette_samples(X, cluster_labels)

    return silhouette_avg, sample_silhouette_values, cluster_labels

def render():
    """Renders the clustering optimization analysis page."""
    st.title("🔬 Clustering Optimization Analysis")
    st.markdown("### Determine optimal number of clusters using Elbow Method and Silhouette Analysis")

    if 'processed_df' not in st.session_state or st.session_state.processed_df is None:
        st.error("No processed data found. Please complete the previous steps.")
        if st.button("⬅️ Back to Target Analysis"):
            st.session_state.step = "target_analysis"
            st.rerun()
        return

    df = st.session_state.processed_df.copy()

    # Data preparation for clustering
    st.subheader("📊 Data Preparation for Clustering")

    # Show original dataframe info
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Rows", len(df))
    with col2:
        st.metric("Total Columns", len(df.columns))
    with col3:
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        st.metric("Numeric Columns", len(numeric_cols))

    # Prepare data for clustering (encode categorical variables)
    st.info("Preparing data for clustering by encoding categorical variables and scaling features...")

    with st.spinner("Encoding categorical variables..."):
        # Create a copy for clustering
        clustering_df = df.copy()
        label_encoders = {}

        # Encode categorical variables
        categorical_cols = clustering_df.select_dtypes(include=['object', 'category']).columns

        for col in categorical_cols:
            le = LabelEncoder()
            clustering_df[col] = le.fit_transform(clustering_df[col].astype(str))
            label_encoders[col] = le

        # Handle missing values
        clustering_df = clustering_df.fillna(clustering_df.mean())

        # Standardize the features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(clustering_df)

        st.success(f"Data prepared successfully! Encoded {len(categorical_cols)} categorical variables.")

    # Display preparation summary
    if len(categorical_cols) > 0:
        with st.expander("View Categorical Encoding Details"):
            for col in categorical_cols:
                unique_values = df[col].unique()[:10]  # Show first 10 unique values
                st.write(f"**{col}**: {len(df[col].unique())} unique values")
                st.write(f"Sample values: {list(unique_values)}")

    # Clustering Analysis Section
    st.divider()
    st.subheader("🔍 Clustering Optimization Analysis")

    # Parameter selection
    col1, col2 = st.columns(2)
    with col1:
        max_clusters = st.slider("Maximum number of clusters to test", 2, 15, 10)
    with col2:
        analysis_type = st.selectbox("Analysis Method", 
                                   ["Both Methods", "Elbow Method Only", "Silhouette Analysis Only"])

    if st.button("🚀 Run Clustering Analysis", type="primary"):

        with st.spinner("Running clustering optimization analysis..."):

            results = {}

            # Elbow Method Analysis
            if analysis_type in ["Both Methods", "Elbow Method Only"]:
                st.subheader("📈 Elbow Method Analysis")

                k_range_elbow, wcss = calculate_wcss(X_scaled, max_clusters)

                # Create elbow plot
                fig_elbow = go.Figure()
                fig_elbow.add_trace(go.Scatter(
                    x=list(k_range_elbow),
                    y=wcss,
                    mode='lines+markers',
                    name='WCSS',
                    line=dict(color='#ff6b6b', width=3),
                    marker=dict(size=8)
                ))

                fig_elbow.update_layout(
                    title="Elbow Method - Within-Cluster Sum of Squares",
                    xaxis_title="Number of Clusters (k)",
                    yaxis_title="WCSS",
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(fig_elbow, use_container_width=True)

                # Calculate elbow point (simple method - look for maximum change in slope)
                if len(wcss) >= 3:
                    differences = np.diff(wcss)
                    second_differences = np.diff(differences)
                    elbow_idx = np.argmax(np.abs(second_differences)) + 2  # +2 because we lost 2 elements
                    elbow_k = k_range_elbow[elbow_idx]

                    st.info(f"🎯 **Suggested optimal k from Elbow Method**: {elbow_k}")
                    results['elbow_optimal_k'] = elbow_k

                # Show WCSS values
                wcss_df = pd.DataFrame({
                    'Number of Clusters': k_range_elbow,
                    'WCSS': wcss,
                    'Reduction from Previous': [0] + [-wcss[i] + wcss[i-1] for i in range(1, len(wcss))]
                })

                with st.expander("View WCSS Details"):
                    st.dataframe(wcss_df, use_container_width=True)

            # Silhouette Analysis
            if analysis_type in ["Both Methods", "Silhouette Analysis Only"]:
                st.subheader("📊 Silhouette Analysis")

                k_range_sil, silhouette_scores = calculate_silhouette_scores(X_scaled, max_clusters)

                # Create silhouette score plot
                fig_sil = go.Figure()
                fig_sil.add_trace(go.Scatter(
                    x=list(k_range_sil),
                    y=silhouette_scores,
                    mode='lines+markers',
                    name='Silhouette Score',
                    line=dict(color='#4ecdc4', width=3),
                    marker=dict(size=8)
                ))

                fig_sil.update_layout(
                    title="Silhouette Analysis - Average Silhouette Score",
                    xaxis_title="Number of Clusters (k)",
                    yaxis_title="Average Silhouette Score",
                    template="plotly_dark",
                    height=500
                )

                st.plotly_chart(fig_sil, use_container_width=True)

                # Find optimal k from silhouette scores
                if silhouette_scores:
                    best_sil_idx = np.argmax(silhouette_scores)
                    best_sil_k = k_range_sil[best_sil_idx]
                    best_sil_score = silhouette_scores[best_sil_idx]

                    st.info(f"🎯 **Suggested optimal k from Silhouette Analysis**: {best_sil_k} (Score: {best_sil_score:.3f})")
                    results['silhouette_optimal_k'] = best_sil_k
                    results['silhouette_best_score'] = best_sil_score

                # Show silhouette scores table
                sil_df = pd.DataFrame({
                    'Number of Clusters': k_range_sil,
                    'Silhouette Score': silhouette_scores
                })

                with st.expander("View Silhouette Scores Details"):
                    st.dataframe(sil_df, use_container_width=True)

            # Detailed Silhouette Analysis for recommended k values
            st.subheader("🔍 Detailed Silhouette Analysis")

            recommended_k_values = []
            if 'elbow_optimal_k' in results:
                recommended_k_values.append(results['elbow_optimal_k'])
            if 'silhouette_optimal_k' in results:
                recommended_k_values.append(results['silhouette_optimal_k'])

            # Remove duplicates and ensure we have valid values
            recommended_k_values = list(set([k for k in recommended_k_values if 2 <= k <= max_clusters]))

            if not recommended_k_values:
                recommended_k_values = [3, 4, 5]  # Default values if nothing found

            # Allow user to select k values for detailed analysis
            selected_k_values = st.multiselect(
                "Select k values for detailed silhouette analysis:",
                options=list(range(2, max_clusters + 1)),
                default=recommended_k_values[:3]  # Limit to first 3
            )

            if selected_k_values:
                for k in selected_k_values:
                    with st.expander(f"Detailed Analysis for k={k}"):
                        silhouette_avg, sample_silhouette_values, cluster_labels = create_silhouette_plot(X_scaled, k)

                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("Average Silhouette Score", f"{silhouette_avg:.3f}")

                            # Cluster sizes
                            unique_labels, counts = np.unique(cluster_labels, return_counts=True)
                            cluster_sizes = pd.DataFrame({
                                'Cluster': unique_labels,
                                'Size': counts,
                                'Percentage': (counts / len(cluster_labels)) * 100
                            })
                            st.dataframe(cluster_sizes, use_container_width=True)

                        with col2:
                            # Create silhouette plot visualization using Plotly
                            silhouette_data = []
                            y_lower = 10

                            for i in range(k):
                                ith_cluster_silhouette_values = sample_silhouette_values[cluster_labels == i]
                                ith_cluster_silhouette_values.sort()

                                size_cluster_i = ith_cluster_silhouette_values.shape[0]
                                y_upper = y_lower + size_cluster_i

                                silhouette_data.extend([
                                    {'y': y, 'silhouette': s, 'cluster': i}
                                    for y, s in zip(range(y_lower, y_upper), ith_cluster_silhouette_values)
                                ])

                                y_lower = y_upper + 10

                            if silhouette_data:
                                sil_df = pd.DataFrame(silhouette_data)
                                fig_detailed = px.scatter(sil_df, x='silhouette', y='y', 
                                                        color='cluster', 
                                                        title=f"Silhouette Plot for k={k}")
                                fig_detailed.add_vline(x=silhouette_avg, line_dash="dash", 
                                                     line_color="red", 
                                                     annotation_text=f"Avg: {silhouette_avg:.3f}")
                                fig_detailed.update_layout(template="plotly_dark", height=400)
                                st.plotly_chart(fig_detailed, use_container_width=True)

            # Final Recommendation
            st.divider()
            st.subheader("🎯 Final Recommendation")

            if analysis_type == "Both Methods" and len(results) >= 2:
                elbow_k = results.get('elbow_optimal_k')
                silhouette_k = results.get('silhouette_optimal_k')

                if elbow_k == silhouette_k:
                    st.success(f"🎉 **Both methods agree!** Recommended number of clusters: **{elbow_k}**")
                    final_k = elbow_k
                else:
                    st.warning(f"Methods disagree: Elbow suggests **{elbow_k}**, Silhouette suggests **{silhouette_k}**")
                    st.info("Consider the silhouette score as it measures both cohesion and separation.")
                    final_k = silhouette_k

                results['final_recommended_k'] = final_k

            elif 'silhouette_optimal_k' in results:
                final_k = results['silhouette_optimal_k']
                st.success(f"🎯 **Recommended number of clusters**: **{final_k}**")
                results['final_recommended_k'] = final_k

            elif 'elbow_optimal_k' in results:
                final_k = results['elbow_optimal_k']
                st.success(f"🎯 **Recommended number of clusters**: **{final_k}**")
                results['final_recommended_k'] = final_k

            else:
                st.warning("Could not determine optimal number of clusters. Consider k=3 as a starting point.")
                results['final_recommended_k'] = 3

            # Store results
            st.session_state.clustering_results = {
                'analysis_results': results,
                'scaled_data': X_scaled,
                'scaler': scaler,
                'label_encoders': label_encoders,
                'original_columns': df.columns.tolist()
            }

            # Show final insights
            st.subheader("💡 Key Insights")
            insights = [
                f"• Analyzed clustering optimization for {len(X_scaled)} data points with {X_scaled.shape[1]} features",
                f"• Tested cluster numbers from 2 to {max_clusters}",
            ]

            if 'silhouette_best_score' in results:
                score = results['silhouette_best_score']
                if score > 0.7:
                    insights.append("• Excellent cluster separation (Silhouette > 0.7)")
                elif score > 0.5:
                    insights.append("• Good cluster separation (Silhouette > 0.5)")
                elif score > 0.25:
                    insights.append("• Reasonable cluster separation (Silhouette > 0.25)")
                else:
                    insights.append("• Weak cluster separation (Silhouette < 0.25) - consider if clustering is appropriate")

            if len(categorical_cols) > 0:
                insights.append(f"• Encoded {len(categorical_cols)} categorical variables for clustering analysis")

            for insight in insights:
                st.markdown(insight)

    # Navigation buttons
    st.divider()
    col1, col2 = st.columns([1, 1])

    with col1:
        if st.button("⬅️ Back to Target Analysis"):
            st.session_state.step = "target_analysis"
            st.rerun()

    with col2:
        if st.button("Continue to Segmentation ➡️"):
            st.session_state.step = "segmentation_choice"
            st.rerun()
