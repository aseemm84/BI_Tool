import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from backend import (
    load_data, clean_data, find_best_columns, calculate_kpis,
    get_contribution_analysis
)

# Set the page configuration for a wide layout and a custom title.
st.set_page_config(layout="wide", page_title="Self-Service BI Dashboard")

# --- Initialize Session State ---
# This is crucial for remembering the user's settings and custom charts.
if 'manual_charts' not in st.session_state:
    st.session_state.manual_charts = []
if 'analysis_mode' not in st.session_state:
    st.session_state.analysis_mode = 'Auto'

# Inject custom CSS for a polished, PowerBI-like appearance.
st.markdown("""
<style>
    .stApp { background-color: #F0F2F6; }
    .kpi-card {
        background-color: #FFFFFF; padding: 20px; border-radius: 10px;
        border: 1px solid #E0E0E0; box-shadow: 0 1px 3px rgba(0,0,0,0.1); text-align: center;
    }
    .kpi-title { font-size: 16px; font-weight: bold; color: #5A5A5A; }
    .kpi-value { font-size: 36px; font-weight: bold; color: #1E1E1E; }
</style>
""", unsafe_allow_html=True)

# --- Main Title ---
st.title("Self-Service BI Dashboard")

# --- File Uploader and Data Loading ---
st.sidebar.title("Controls")
uploaded_file = st.sidebar.file_uploader("Upload your data (CSV)", type=["csv"])

if uploaded_file is None:
    st.info("Please upload a CSV file to begin.")
    st.stop()

# Cache the data loading and cleaning process to improve performance.
@st.cache_data
def load_and_process_data(file):
    raw_df = load_data(file)
    if isinstance(raw_df, str): return raw_df, None
    cleaned_df = clean_data(raw_df.copy())
    return raw_df, cleaned_df

df_raw, df = load_and_process_data(uploaded_file)

if isinstance(df_raw, str):
    st.error(df_raw)
    st.stop()

# --- Main Mode Selector ---
st.session_state.analysis_mode = st.sidebar.radio(
    "Select Mode", ('Auto', 'Manual'),
    help="**Auto:** The app generates a dashboard automatically. **Manual:** Build your own dashboard from scratch."
)

# --- AUTO MODE LOGIC ---
if st.session_state.analysis_mode == 'Auto':
    st.header("Automated Dashboard")
    st.write("This dashboard was generated automatically based on the most relevant columns found in your data.")
    
    date_col, value_col, category_col = find_best_columns(df)
    if not all([date_col, value_col, category_col]):
        st.error("Auto-detection failed. Could not find suitable columns for a dashboard. Please try Manual Mode.")
        st.stop()

    # Display KPIs
    kpis = calculate_kpis(df, date_col, value_col)
    cols = st.columns(len(kpis))
    for i, (title, value) in enumerate(kpis.items()):
        with cols[i]:
            st.markdown(f'<div class="kpi-card"><div class="kpi-title">{title}</div><div class="kpi-value">{value}</div></div>', unsafe_allow_html=True)
    
    st.markdown("<hr>", unsafe_allow_html=True)
    
    # Display Charts
    col1, col2 = st.columns(2)
    with col1:
        st.subheader(f"Trend of {value_col}")
        monthly_data = df.set_index(date_col)[value_col].resample('M').sum().reset_index()
        fig = px.line(monthly_data, x=date_col, y=value_col)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        st.subheader(f"Contribution by {category_col}")
        contrib_df = get_contribution_analysis(df, category_col, value_col)
        fig2 = px.pie(contrib_df.head(10), names=category_col, values=value_col, hole=0.4)
        st.plotly_chart(fig2, use_container_width=True)

# --- MANUAL MODE LOGIC ---
else:
    st.header("Manual Dashboard Builder")
    st.write("Design your own dashboard. Add up to 10 charts using the builder below.")
    
    # --- Chart Builder in Sidebar ---
    st.sidebar.header("Chart Builder")
    
    chart_type = st.sidebar.selectbox("1. Select Chart Type", 
                                      ["KPI Card", "Bar Chart", "Line Chart", "Donut Chart", "Data Table"])
    
    # These lists are used for the column selection dropdowns.
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64[ns]']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    config = {"type": chart_type, "cols": {}}

    # This block shows different column selectors based on the chosen chart type.
    st.sidebar.write("2. Configure Columns")
    if chart_type == "KPI Card":
        config["cols"]["value"] = st.sidebar.selectbox("Select Metric", numeric_cols)
        config["title"] = st.sidebar.text_input("Card Title", f"Total {config['cols']['value']}")
    elif chart_type == "Bar Chart":
        config["cols"]["x"] = st.sidebar.selectbox("Select Category (X-axis)", categorical_cols)
        config["cols"]["y"] = st.sidebar.selectbox("Select Metric (Y-axis)", numeric_cols)
    elif chart_type == "Line Chart":
        config["cols"]["x"] = st.sidebar.selectbox("Select Date (X-axis)", date_cols)
        config["cols"]["y"] = st.sidebar.selectbox("Select Metric (Y-axis)", numeric_cols)
    elif chart_type == "Donut Chart":
        config["cols"]["names"] = st.sidebar.selectbox("Select Category", categorical_cols)
        config["cols"]["values"] = st.sidebar.selectbox("Select Metric", numeric_cols)
    elif chart_type == "Data Table":
        config["cols"]["all"] = st.sidebar.multiselect("Select columns to display", df.columns.tolist())

    # The button to add the configured chart to the dashboard.
    if st.sidebar.button("Add Chart to Dashboard"):
        if len(st.session_state.manual_charts) < 10:
            st.session_state.manual_charts.append(config)
        else:
            st.sidebar.warning("Maximum of 10 charts reached.")

    st.sidebar.markdown("---")
    
    # --- Display and Manage Added Charts ---
    st.sidebar.header("Your Dashboard Layout")
    if not st.session_state.manual_charts:
        st.sidebar.info("No charts added yet.")
    
    for i, chart_conf in enumerate(st.session_state.manual_charts):
        # Creates a small entry for each added chart in the sidebar.
        cols = st.sidebar.columns([4, 1])
        cols[0].write(f"**{i+1}.** {chart_conf.get('title', chart_conf['type'])}")
        # The 'Remove' button removes the chart from the session state list.
        if cols[1].button("X", key=f"remove_{i}"):
            st.session_state.manual_charts.pop(i)
            st.experimental_rerun()

    # --- Render the User-Built Dashboard ---
    if not st.session_state.manual_charts:
        st.info("Your custom dashboard is empty. Use the 'Chart Builder' in the sidebar to add visuals.")
    else:
        # Create a dynamic grid layout. This example uses 2 columns.
        num_charts = len(st.session_state.manual_charts)
        cols = st.columns(2)
        
        for i, chart_conf in enumerate(st.session_state.manual_charts):
            container = cols[i % 2] # Distribute charts between the two columns
            with container:
                try:
                    # This is the main rendering logic for the manual dashboard.
                    if chart_conf["type"] == "KPI Card":
                        value = df[chart_conf["cols"]["value"]].sum()
                        st.markdown(f'<div class="kpi-card"><div class="kpi-title">{chart_conf["title"]}</div><div class="kpi-value">${value:,.2f}</div></div>', unsafe_allow_html=True)
                        st.write("") # Add some space
                    
                    elif chart_conf["type"] == "Bar Chart":
                        st.subheader(f"Bar Chart: {chart_conf['cols']['y']} by {chart_conf['cols']['x']}")
                        grouped_df = df.groupby(chart_conf['cols']['x'])[chart_conf['cols']['y']].sum().reset_index()
                        fig = px.bar(grouped_df, x=chart_conf['cols']['x'], y=chart_conf['cols']['y'])
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_conf["type"] == "Line Chart":
                        st.subheader(f"Line Chart: {chart_conf['cols']['y']} over time")
                        fig = px.line(df, x=chart_conf['cols']['x'], y=chart_conf['cols']['y'])
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_conf["type"] == "Donut Chart":
                        st.subheader(f"Donut Chart: {chart_conf['cols']['values']} by {chart_conf['cols']['names']}")
                        fig = px.pie(df, names=chart_conf['cols']['names'], values=chart_conf['cols']['values'], hole=0.4)
                        st.plotly_chart(fig, use_container_width=True)

                    elif chart_conf["type"] == "Data Table":
                        st.subheader("Data Table")
                        st.dataframe(df[chart_conf["cols"]["all"]])

                except Exception as e:
                    st.error(f"Could not render chart #{i+1}. Error: {e}")
