import streamlit as st

def reset_app():
    """Clears all session state variables and reruns the app."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def render():
    """Renders the welcome page of the application."""
    st.title("🚀 Advanced Business Intelligence Tool")
    st.markdown("#### Transform your CSV or Excel data into beautiful, interactive dashboards in minutes.")

    st.markdown("""
    <div style="display: flex; justify-content: space-around; margin: 2rem 0;">
        <div style="text-align: center; padding: 1rem;">
            <h3>🤖</h3>
            <h4>Automated</h4>
            <p>Data Processing</p>
        </div>
        <div style="text-align: center; padding: 1rem;">
            <h3>🧠</h3>
            <h4>AI-Powered</h4>
            <p>Insights</p>
        </div>
        <div style="text-align: center; padding: 1rem;">
            <h3>⚡</h3>
            <h4>Effortless</h4>
            <p>Workflow</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # New workflow overview
    st.subheader("🛣️ Your Data Journey")
    st.markdown("""
    **Workflow**

    1. **📁 Upload Data** - CSV or Excel files
    2. **🔧 Declare Data Types** - Optimize column types for analysis  
    3. **⚙️ Automated Processing** - Cleaning, analysis & feature engineering
    4. **📊 Data Profiling** - Comprehensive data quality report with visual charts
    5. **🛠️ Manual Features** - Create custom domain-specific features
    6. **🎯 Target Analysis** - Select target variable & analyze drivers with detailed reports
    7. **🔬 Clustering Analysis** - **BOTH** Elbow & Silhouette methods for optimal clusters
    8. **🎨 Segmentation** - Apply intelligent data segmentation
    9. **📈 Dashboard Creation** - **ALL** chart types + Storytelling Assistant + Export options
    """)

    if st.button("🚀 Launch Application", type="primary"):
        st.session_state.step = "upload"
        st.rerun()

    st.markdown("""
    <div style="margin-top: 3rem; text-align: center;">
        <a href="https://github.com/aseemm84/Enhanced-Business-Intelligence-App" target="_blank">
            📚 View Project on GitHub / ReadMe
        </a>
        <br><br>
        <p>Created by <strong>Aseem Mehrotra</strong> | 
        <a href="https://linkedin.com/in/aseem-mehrotra" target="_blank">LinkedIn Profile</a></p>
    </div>
    """, unsafe_allow_html=True)
