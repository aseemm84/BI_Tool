import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import base64
import re
import io

from backend import cleaning, analysis, engineering, utils, narratives

# --- Helper Functions ---
def reset_app():
    """Clears all session state variables and reruns the app."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def get_category_colors(chart_config: dict, df: pd.DataFrame) -> dict:
    """
    Manages color customization for categorical charts.
    
    Args:
        chart_config: The configuration dictionary for the chart.
        df: The dataframe used for the chart.

    Returns:
        A dictionary mapping categories to colors.
    """
    color_col = None
    # Determine which column is being used for color
    if chart_config['type'] in ["Bar Chart", "Line Chart"] and 'color' in chart_config:
        color_col = chart_config.get('color')
    elif chart_config['type'] in ["Donut Chart", "Funnel Chart", "Treemap", "Sunburst Chart"]:
        color_col = chart_config.get('names') or (chart_config.get('path') and chart_config.get('path')[0])

    if color_col and df[color_col].dtype in ['object', 'category']:
        if 'colors' not in chart_config:
            chart_config['colors'] = {}
            
        unique_categories = df[color_col].unique()
        default_colors = px.colors.qualitative.Plotly
        with st.expander("Customize Colors"):
            for i, category in enumerate(unique_categories):
                # Use a regex to create a valid key from the category name
                key_safe_category = re.sub(r'[^A-Za-z0-9]+', '', str(category))
                color_key = f"color_{chart_config['id']}_{key_safe_category}"
                # Set default color if not already set
                if category not in chart_config['colors']:
                    chart_config['colors'][category] = default_colors[i % len(default_colors)]
                
                chart_config['colors'][category] = st.color_picker(
                    f"Color for {category}", 
                    value=chart_config['colors'][category], 
                    key=color_key
                )
        return chart_config['colors']
    return None

def render_dashboard_layout(charts: list, df: pd.DataFrame):
    """
    Renders the charts in a dynamic grid layout based on their specified sizes.
    """
    if not charts:
        st.info("Your dashboard is empty. Add some charts from the sidebar!")
        return

    row_buffer = []
    current_width = 0
    MAX_WIDTH = 100

    for i, chart_config in enumerate(charts):
        chart_size = chart_config.get('size', 50) # Default to 50% width

        if current_width + chart_size > MAX_WIDTH:
            # Render the current row buffer
            cols = st.columns([c.get('size', 50) for c in row_buffer])
            for j, c_config in enumerate(row_buffer):
                with cols[j]:
                    render_chart(c_config, df)
            # Reset buffer for the new row
            row_buffer = [chart_config]
            current_width = chart_size
        else:
            # Add to current row buffer
            row_buffer.append(chart_config)
            current_width += chart_size
    
    # Render any remaining charts in the buffer
    if row_buffer:
        cols = st.columns([c.get('size', 50) for c in row_buffer])
        for j, c_config in enumerate(row_buffer):
            with cols[j]:
                render_chart(c_config, df)


def render_chart(chart_config: dict, df: pd.DataFrame):
    """Renders a single chart container."""
    is_presentation_mode = st.query_params.get("present") == "true"
    with st.container(border=True):
        st.subheader(chart_config.get('title', 'Chart'))
        try:
            # All charts will use the dark theme now
            plotly_template = 'plotly_dark'
            fig = None
            narrative_text = ""

            # Get custom colors if applicable
            color_map = get_category_colors(chart_config, df)

            # Handle Data Table separately
            if chart_config['type'] == "Data Table":
                # FIX: Convert category columns to string to prevent Arrow conversion error
                table_df = df[chart_config.get('columns', df.columns)].copy()
                for col in table_df.select_dtypes(include='category').columns:
                    table_df[col] = table_df[col].astype(str)
                st.dataframe(table_df, use_container_width=True)
                narrative_text = f"Displaying {len(chart_config.get('columns', df.columns))} selected columns."
            else:
                # Build chart with Plotly
                kwargs = {'color_discrete_map': color_map} if color_map else {}
                if 'color' in chart_config and chart_config['color']:
                    kwargs['color'] = chart_config['color']

                if chart_config['type'] == "Heatmap":
                    corr = df[utils.get_chart_compatible_columns(df, 'Heatmap')['numeric_only']].corr()
                    fig = px.imshow(corr, text_auto=True, aspect="auto")
                elif chart_config['type'] == "Gantt Chart":
                    fig = px.timeline(df, x_start=chart_config['Start'], x_end=chart_config['Finish'], y=chart_config['Task'], **kwargs)
                elif chart_config['type'] == "Bar Chart": 
                    fig = px.bar(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)
                elif chart_config['type'] == "Line Chart": 
                    fig = px.line(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)
                elif chart_config['type'] == "Scatter Plot": 
                    fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)
                elif chart_config['type'] == "3D Scatter Plot": 
                    fig = px.scatter_3d(df, x=chart_config.get('x'), y=chart_config.get('y'), z=chart_config.get('z'), **kwargs)
                elif chart_config['type'] == "Bubble Chart":
                     fig = px.scatter(df, x=chart_config.get('x'), y=chart_config.get('y'), size=chart_config.get('size_col'), color=chart_config.get('color'))
                elif chart_config['type'] == "Donut Chart": 
                    fig = px.pie(df, names=chart_config.get('names'), values=chart_config.get('values'), hole=0.5, **kwargs)
                elif chart_config['type'] == "Funnel Chart":
                    fig = px.funnel(df, x=chart_config.get('values'), y=chart_config.get('names'), **kwargs)
                elif chart_config['type'] == "Treemap": 
                    fig = px.treemap(df, path=chart_config.get('path'), values=chart_config.get('values'), **kwargs)
                elif chart_config['type'] == "Sunburst Chart": 
                    fig = px.sunburst(df, path=chart_config.get('path'), values=chart_config.get('values'), **kwargs)
                elif chart_config['type'] == "Violin Chart": 
                    fig = px.violin(df, x=chart_config.get('x'), y=chart_config.get('y'), box=True, **kwargs)
                elif chart_config['type'] == "Box Plot":
                    fig = px.box(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)
                elif chart_config['type'] == "Histogram":
                    fig = px.histogram(df, x=chart_config.get('x'), y=chart_config.get('y'), **kwargs)

                if fig:
                    # FIX: Explicitly set font and line colors for visibility
                    fig.update_layout(
                        template=plotly_template,
                        title_text="",
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)',
                        font_color="white",
                        xaxis=dict(
                            gridcolor='rgba(255, 255, 255, 0.3)',
                            linecolor='white',
                            title_font_color="white",
                            tickfont_color="white"
                        ),
                        yaxis=dict(
                            gridcolor='rgba(255, 255, 255, 0.3)',
                            linecolor='white',
                            title_font_color="white",
                            tickfont_color="white"
                        ),
                        legend_font_color="white",
                        legend_title_font_color="white"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                narrative_text = narratives.generate_narrative(chart_config, df)

            st.markdown(f"**💡 Insight:** {narrative_text}")

        except Exception as e: 
            st.error(f"Could not create chart '{chart_config.get('title')}': {e}")
        
        if not is_presentation_mode:
            # Chart controls (size, remove)
            c1, c2 = st.columns([3, 1])
            chart_config['size'] = c1.slider("Chart Size (%)", 10, 100, chart_config.get('size', 50), key=f"size_{chart_config['id']}")
            if c2.button("🗑️ Remove", key=f"del_{chart_config['id']}", use_container_width=True):
                st.session_state.charts = [c for c in st.session_state.charts if c['id'] != chart_config['id']]
                st.rerun()

# --- Page Configuration ---
st.set_page_config(page_title="Advanced Business Intelligence Tool", page_icon="🚀", layout="wide")

# --- Session State Initialization ---
if 'step' not in st.session_state: st.session_state.step = "welcome"
if 'processed_df' not in st.session_state: st.session_state.processed_df = None
if 'charts' not in st.session_state: st.session_state.charts = []
if 'kpi_cards' not in st.session_state: st.session_state.kpi_cards = []
if 'processing_log' not in st.session_state: st.session_state.processing_log = {}
if 'story_suggestion' not in st.session_state: st.session_state.story_suggestion = ""
if 'chart_id_counter' not in st.session_state: st.session_state.chart_id_counter = 0
if 'dashboard_settings' not in st.session_state:
    st.session_state.dashboard_settings = {
        'layout': '1920x1080 (Full HD)',
    }
# New session state variables for file handling
if 'uploaded_file_data' not in st.session_state: st.session_state.uploaded_file_data = None
if 'sheet_names' not in st.session_state: st.session_state.sheet_names = None


# --- Main App Logic ---
is_presentation_mode = st.query_params.get("present") == "true"

# Apply custom CSS for the new theme
st.markdown("""
<style>
    /* Main background gradient */
    .stApp {
        background: linear-gradient(135deg, #4a00e0 0%, #8e2de2 100%);
        color: white;
    }

    /* Main content area styling */
    .main .block-container {
        background-color: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 2rem;
        backdrop-filter: blur(10px);
    }

    /* Sidebar styling - using stable data-testid selector */
    [data-testid="stSidebar"] {
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }

    /* Button styling to match the image - targets regular, download, and form submit buttons */
    .stButton>button, [data-testid="stDownloadButton"] button, [data-testid="stFormSubmitButton"] button {
        background: linear-gradient(90deg, #ff0084, #f44336);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 12px 24px;
        font-weight: bold;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%;
    }
    .stButton>button:hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stFormSubmitButton"] button:hover {
        transform: scale(1.05);
        box-shadow: 0 0 15px #ff0084;
    }

    /* General text color */
    body, p, label {
        color: white;
    }
    h1, h2, h3, h4, h5, h6 {
        color: white !important;
    }
    
    /* Text color for sidebar */
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] * {
        color: white !important;
    }
    /* Style for containers and expanders */
    [data-testid="stVerticalBlock"], [data-testid="stExpander"] {
        border: 1px solid rgba(255, 255, 255, 0.2);
        background-color: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
    }
    
    /* Style for metric cards */
    [data-testid="stMetric"] {
         background-color: rgba(255, 255, 255, 0.1);
         border-radius: 10px;
         padding: 1rem;
    }
    
    /* Style for file uploader */
    [data-testid="stFileUploader"] {
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    /* Ensure selectbox dropdowns are readable */
    .st-emotion-cache-1jicfl2 {
        background-color: #4a00e0;
    }

</style>
""", unsafe_allow_html=True)


# Step 1: Welcome Screen
if st.session_state.step == "welcome":
    st.title("🚀 Advanced Business Intelligence Tool")
    st.markdown("#### Transform your CSV or Excel data into beautiful, interactive dashboards in minutes.")
    
    st.markdown("""
        <div style="display: flex; justify-content: space-around; padding: 2rem 0;">
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">15+</h2>
                <p>Chart Types</p>
            </div>
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">28</h2>
                <p>Features</p>
            </div>
            <div style="text-align: center;">
                <h2 style="color: #ff0084;">8</h2>
                <p>Step Workflow</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Launch Application", type="primary"):
        st.session_state.step = "upload"
        st.rerun()
    
    # FIX: Added the GitHub/README link back
    st.markdown("""<div style="text-align: center; padding-top: 1rem;"><a href="https://github.com/aseemm84/Business-Intelligence-App" target="_blank" style="color: #ff0084;">View Project on GitHub / ReadMe</a></div>""", unsafe_allow_html=True)

    st.markdown("""<div style="text-align: center; padding-top: 1rem;"><p>Created by Aseem Mehrotra | <a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank" style="color: #ff0084;">LinkedIn Profile</a></p></div>""", unsafe_allow_html=True)


# Step 2: File Upload
elif st.session_state.step == "upload":
    st.title("1. Upload Your Data")
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            # Store the file in session state to persist it
            st.session_state.uploaded_file_data = uploaded_file.getvalue()
            file_name = uploaded_file.name

            if file_name.endswith('.csv'):
                # For CSV, read it directly
                st.session_state.raw_df = pd.read_csv(io.BytesIO(st.session_state.uploaded_file_data))
                st.session_state.step = "processing"
                st.rerun()
            
            elif file_name.endswith('.xlsx'):
                # For Excel, first get sheet names
                excel_file = pd.ExcelFile(io.BytesIO(st.session_state.uploaded_file_data))
                st.session_state.sheet_names = excel_file.sheet_names
                
                if len(st.session_state.sheet_names) == 1:
                    # If only one sheet, load it automatically
                    st.session_state.raw_df = pd.read_excel(excel_file, sheet_name=st.session_state.sheet_names[0])
                    st.session_state.step = "processing"
                    st.rerun()
                else:
                    # If multiple sheets, move to sheet selection step
                    st.session_state.step = "select_sheet"
                    st.rerun()

        except Exception as e: 
            st.error(f"Error reading file: {e}")
    
    if st.button("⬅️ Back to Welcome"): 
        reset_app()

# Step 2b: Select Sheet (for multi-sheet Excel files)
elif st.session_state.step == "select_sheet":
    st.title("2. Select a Sheet")
    st.info("Your Excel file contains multiple sheets. Please select one to analyze.")
    
    selected_sheet = st.selectbox(
        "Available Sheets",
        options=st.session_state.sheet_names
    )
    
    if st.button("Load Sheet and Continue", type="primary"):
        try:
            # Load the selected sheet into the raw_df
            excel_file = pd.ExcelFile(io.BytesIO(st.session_state.uploaded_file_data))
            st.session_state.raw_df = pd.read_excel(excel_file, sheet_name=selected_sheet)
            st.session_state.step = "processing"
            st.rerun()
        except Exception as e:
            st.error(f"Could not load sheet '{selected_sheet}': {e}")
            
    if st.button("⬅️ Back to Upload"):
        st.session_state.step = "upload"
        # Clear sheet-related state
        if 'sheet_names' in st.session_state: del st.session_state.sheet_names
        if 'uploaded_file_data' in st.session_state: del st.session_state.uploaded_file_data
        st.rerun()


# Step 3: Automated Processing
elif st.session_state.step == "processing":
    st.title("⚙️ Processing Your Data...")
    if 'raw_df' in st.session_state:
        with st.spinner("Cleaning data and removing useless columns..."):
            cleaned_df, log1 = cleaning.clean_data(st.session_state.raw_df.copy())
        with st.spinner("Performing advanced analysis..."):
            _, log2 = analysis.run_full_analysis(cleaned_df)
        with st.spinner("Engineering new features and measures..."):
            engineered_df, log3 = engineering.engineer_features_automated(cleaned_df)
        st.session_state.processing_log = {**log1, **log2, **log3}
        st.session_state.processed_df = engineered_df
        st.session_state.step = "profiling_report"
        st.balloons()
        st.rerun()

# Step 4: Profiling Report
elif st.session_state.step == "profiling_report":
    st.title("📊 Data Profiling Report")
    st.info("Here's a summary of the automated actions performed on your data.")
    log = st.session_state.processing_log
    
    # Display log metrics
    cols = st.columns(4)
    cols[0].metric("Missing Values Filled", log.get('missing_values_filled', 0))
    cols[1].metric("Duplicate Rows Removed", log.get('duplicates_removed', 0))
    cols[2].metric("Potential Outliers", log.get('outliers_identified', 0))
    cols[3].metric("New Features Engineered", log.get('features_engineered', 0))
    
    if log.get('useless_columns_removed'):
        st.warning(f"Removed useless columns: {', '.join(log['useless_columns_removed'])}")

    # Display Automated Measures
    if 'measures' in log and log['measures']:
        st.subheader("Automated Measures")
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

    st.subheader("Key Driver Analysis")
    numeric_cols = st.session_state.processed_df.select_dtypes(include=np.number).columns.tolist()
    target_variable = st.selectbox("Select Target Variable to Analyze", options=[None] + numeric_cols)
    if target_variable:
        drivers = analysis.find_key_drivers(st.session_state.processed_df, target_variable)
        if drivers is not None: st.dataframe(drivers.rename("Correlation Strength"))
    if st.button("Continue to Manual Feature Creation ➡️", type="primary"):
        st.session_state.step = "manual_feature_creation"
        st.rerun()

# Step 5: Manual Feature Creation
elif st.session_state.step == "manual_feature_creation":
    st.title("🛠️ Manual Feature Creation")
    st.write("Create your own features to add to the dataset.")
    
    df = st.session_state.processed_df
    numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
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
        
        elif feature_type == "Unary Transformation (1 column)":
            st.subheader("Unary Transformation")
            col = st.selectbox("Select a numeric column", numeric_cols)
            operation = st.selectbox("Select operation", ['log', 'square', 'sqrt', 'average'])
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'unary', 'col': col, 'op': operation}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {operation}_of_{col}")

        elif feature_type == "Categorical Counts":
            st.subheader("Categorical Counts")
            col = st.selectbox("Select a categorical column", categorical_cols)
            submitted = st.form_submit_button("Create Feature")
            if submitted:
                feature_def = {'type': 'categorical_count', 'col': col}
                st.session_state.processed_df = engineering.create_custom_feature(df, feature_def)
                st.success(f"Created feature: {col}_counts")

    # FIX: Convert category columns to string for display to prevent Arrow conversion error
    df_display = st.session_state.processed_df.head().copy()
    for col in df_display.select_dtypes(include='category').columns:
        df_display[col] = df_display[col].astype(str)
    st.dataframe(df_display)
    
    if st.button("Continue to Segmentation ➡️", type="primary"):
        st.session_state.step = "segmentation_choice"
        st.rerun()

# Step 6: Segmentation Choice
elif st.session_state.step == "segmentation_choice":
    st.title("🔬 Automated Segmentation")
    n_clusters = st.slider("How many segments to find?", 2, 10, 4)
    c1, c2 = st.columns(2)
    if c1.button("Yes, Create Segments", type="primary"):
        with st.spinner("Performing segmentation..."):
            df, log = engineering.perform_segmentation(st.session_state.processed_df, n_clusters)
            st.session_state.processed_df = df
            st.session_state.processing_log.update(log)
        st.session_state.step = "dashboard"
        st.rerun()
    if c2.button("No, Skip to Dashboard"):
        st.session_state.step = "dashboard"
        st.rerun()

# Step 7: Dashboard
elif st.session_state.step == "dashboard":
    if not is_presentation_mode:
        st.title("🎨 Your Interactive Dashboard")
        if st.session_state.charts:
            if st.button("Present 📽️"):
                st.query_params["present"] = "true"
                st.rerun()
    else:
        if st.button("⬅️ Exit Presentation"):
            st.query_params.clear()
            st.rerun()

    df = st.session_state.processed_df
    if not is_presentation_mode:
        with st.sidebar:
            st.header("Dashboard Controls")
            if st.button("🔄 Reset Dashboard", use_container_width=True): 
                st.session_state.charts = []
                st.session_state.kpi_cards = []
                st.session_state.story_suggestion = ""
            
            with st.expander("Dashboard Settings", expanded=True):
                st.session_state.dashboard_settings['layout'] = st.selectbox(
                    "Layout Resolution",
                    options=['1366x768', '1440x900', '1920x1080 (Full HD)', '2560x1440 (QHD)', '3840x2160 (4K UHD)'],
                    index=2
                )

            st.header("KPI Cards")
            available_measures = list(st.session_state.get('available_measures', {}).keys())
            selected_kpis = st.multiselect(
                "Select up to 3 measures for KPI cards",
                options=available_measures,
                default=st.session_state.get('kpi_cards', []),
                max_selections=3
            )
            st.session_state.kpi_cards = selected_kpis

            st.header("Storytelling Assistant")
            if len(st.session_state.charts) >= 4:
                if st.button("💡 Suggest Story Order", use_container_width=True):
                    st.session_state.story_suggestion = narratives.generate_story_suggestion(st.session_state.charts)
                
                if st.session_state.story_suggestion:
                    st.markdown(st.session_state.story_suggestion)
                    with st.expander("Arrange Your Dashboard", expanded=True):
                        chart_titles = [c['title'] for c in st.session_state.charts]
                        ordered_titles = st.multiselect(
                            "Select the order of your charts:",
                            options=chart_titles,
                            default=chart_titles
                        )
                        if st.button("Update Dashboard Layout", use_container_width=True):
                            chart_map = {c['title']: c for c in st.session_state.charts}
                            st.session_state.charts = [chart_map[title] for title in ordered_titles]
                            st.rerun()
            else:
                st.info("Add at least 4 charts to enable the Storytelling Assistant.")


            st.header("Export Options")
            st.download_button(label="📥 Download Processed Data (Excel)", data=utils.to_excel(df), file_name="processed_data.xlsx", mime="application/vnd.ms-excel", use_container_width=True)
            
            st.header("Add a New Chart")
            if len(st.session_state.charts) >= 10:
                st.warning("Maximum of 10 charts reached.")
            else:
                chart_types = ["Bar Chart", "Line Chart", "Scatter Plot", "3D Scatter Plot", "Donut Chart", "Data Table", "Bubble Chart", "Box Plot", "Histogram", "Violin Chart", "Treemap", "Heatmap", "Sunburst Chart", "Funnel Chart", "Gantt Chart"]
                
                chart_type = st.selectbox("Select Chart Type", sorted(chart_types), key="chart_type_selector")
                
                with st.form(key=f"chart_form_{chart_type}", clear_on_submit=True):
                    st.subheader(f"Configure {chart_type}")
                    
                    
                    # Use a sequential counter for unique IDs instead of random numbers
                    chart_id = st.session_state.chart_id_counter
                    chart_config = {'type': chart_type, 'id': f"chart_{chart_id}"}
                    
                    chart_config['title'] = st.text_input("Chart Title", value=f"New {chart_type}")
                    compatible_cols = utils.get_chart_compatible_columns(df, chart_type)
                    
                    if chart_type in ["Bar Chart", "Line Chart", "Histogram", "Box Plot", "Violin Chart"]:
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('x', []))
                    elif chart_type == "Scatter Plot":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('color', []))
                    elif chart_type == "3D Scatter Plot":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['z'] = st.selectbox("Z-axis", compatible_cols.get('z', []))
                        chart_config['color'] = st.selectbox("Color by (optional)", [None] + compatible_cols.get('color', []))
                    elif chart_type == "Bubble Chart":
                        chart_config['x'] = st.selectbox("X-axis", compatible_cols.get('x', []))
                        chart_config['y'] = st.selectbox("Y-axis", compatible_cols.get('y', []))
                        chart_config['size_col'] = st.selectbox("Size", compatible_cols.get('size', []))
                        chart_config['color'] = st.selectbox("Color", compatible_cols.get('color', []))
                    elif chart_type == "Data Table":
                        all_cols = compatible_cols.get('all', [])
                        chart_config['columns'] = st.multiselect("Select columns", all_cols, default=all_cols[:5])
                    elif chart_type in ["Donut Chart", "Funnel Chart"]:
                        chart_config['names'] = st.selectbox("Categories", compatible_cols.get('names', []))
                        chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))
                    elif chart_type in ["Treemap", "Sunburst Chart"]:
                        path_cols = compatible_cols.get('path', [])
                        chart_config['path'] = st.multiselect("Hierarchy Path", path_cols, default=path_cols[:2])
                        chart_config['values'] = st.selectbox("Values", compatible_cols.get('values', []))
                    elif chart_type == "Gantt Chart":
                        chart_config['Task'] = st.selectbox("Task Column", compatible_cols.get('Task', []))
                        chart_config['Start'] = st.selectbox("Start Date Column", compatible_cols.get('Start', []))
                        chart_config['Finish'] = st.selectbox("Finish Date Column", compatible_cols.get('Finish', []))
                    
                    if st.form_submit_button("Add Chart to Dashboard"):
                        st.session_state.charts.append(chart_config)
                        st.session_state.chart_id_counter += 1 # Increment the counter
                        st.rerun()

            st.sidebar.markdown("---")
            st.sidebar.markdown("""<div style="text-align: center; padding-top: 10px;"><p style="margin-bottom: 5px;">Created by Aseem Mehrotra</p><a href="https://www.linkedin.com/in/aseem-mehrotra" target="_blank" style="color: #ff0084;">LinkedIn Profile</a></div>""", unsafe_allow_html=True)

    # --- Main dashboard area ---
    
    if st.session_state.kpi_cards:
        kpi_cols = st.columns(len(st.session_state.kpi_cards))
        all_measures = st.session_state.get('available_measures', {})
        for i, kpi_name in enumerate(st.session_state.kpi_cards):
            with kpi_cols[i]:
                value = all_measures.get(kpi_name, 0)
                formatted_value = f"{value:,.2f}" if isinstance(value, float) else f"{value:,}"
                st.metric(label=kpi_name, value=formatted_value)
        st.markdown("---")

    render_dashboard_layout(st.session_state.charts, df)
