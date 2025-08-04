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
        <div style="display: flex; justify-content: space-around; padding: 2rem 0;">
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">Automated</h2>
                <p>Visualizations</p>
            </div>
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">AI-Powered</h2>
                <p>Insights</p>
            </div>
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">Effortless</h2>
                <p>Workflow</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Application", type="primary"):
        st.session_state.step = "upload"
        st.rerun()

    st.markdown("""<div style="text-align: center; padding-top: 1rem;"><a href="https://github.com/aseemm84/Business-Intelligence-App/blob/main/reademe.md" target="_blank" style="color: #ff0084;">View Project on GitHub / ReadMe</a></div>""", unsafe_allow_html=True)
    st.markdown("""<div style="text-align: center; padding-top: 1rem;"><p>Created by Aseem Mehrotra | <a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank" style="color: #ff0084;">LinkedIn Profile</a></p></div>""", unsafe_allow_html=True)

