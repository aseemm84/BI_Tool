# 🚀 Advanced BI Tool with Automated Analytics

Welcome to the Advanced BI Tool, a powerful, open-source application built with Streamlit that transforms raw data into insightful, presentation-ready dashboards in minutes. This tool is designed to act as an Automated Data Analyst Assistant, guiding you from a simple CSV file to a fully interactive dashboard with minimal effort.

## ✨ Key Features

This tool automates the most time-consuming steps of the data analysis workflow:

**🤖 Automated Data Cleaning**: Intelligently handles missing values by filling them with the median (for numbers) or mode (for categories/dates), removes duplicate rows, and automatically drops useless identifier-like columns (e.g., IDs, serial numbers).

**🔬 Automated Analysis**: Instantly runs a key driver analysis to find the most influential variables correlated with a target you select. It also uses a machine learning model (Isolation Forest) to flag potential outliers in your data.

**🛠️ Hybrid Feature Engineering**: Automatically creates new features using `featuretools` (e.g., `SUM`, `MULTIPLY`) and provides an intuitive UI for you to manually create custom features based on your domain knowledge. You can perform arithmetic between columns, apply transformations (log, square root), or create counts from categories.

**📈 Automated Segmentation**: Uses K-Means clustering to discover hidden customer or data segments automatically. Simply choose the number of segments, and the tool adds a new "Segment" column to your dataset.

**💡 Automated Narratives**: Generates plain-English text summaries for every chart, explaining the key insight so you don't have to. It can identify trends, correlations, and key contributors in your visualizations.

**🎨 Interactive & Customizable Dashboards**: Build beautiful, interactive dashboards with a wide variety of charts (Bar, Line, Scatter, Donut, Heatmap, and more). Customize the layout, theme, colors, and even enter a full-screen "Presentation Mode" for a clean, professional look.

**Story Teeling Assistant**: Get AI-powered suggestions on how to arrange your charts to tell a compelling story, helping you structure your presentation for maximum impact.

## 🗺️  How to Use the App: A Step-by-Step Guide

➡️ Launch the BI Tool (<- https://data-bi-tool.streamlit.app/)

## 🗺️ How to Use the App: A Step-by-Step Guide

The application follows a simple, guided workflow.

### Step 1: Upload Your Data

Start by uploading your dataset. The application currently supports CSV files.

### Step 2: Automated Processing & Profiling

The tool automatically cleans your data, runs an analysis, and engineers new features. You will then be presented with a **Data Profiling Report**.

- Review key metrics like missing values filled and duplicates removed.
- See which columns (if any) were identified as useless and removed.
- Explore the **Automated Measures** (like "Sum of Sales" or "Average Age") that were created.
- Use the Key Driver Analysis to select a target variable and see which features have the strongest correlation with it.

### Step 3: Manual Feature Creation (Optional)

If you have specific domain knowledge, you can create your own features.

- Perform arithmetic between two columns (e.g., `revenue - cost`).
- Apply transformations to a single column (e.g., `log(sales)`).
- Create counts based on categorical columns.

### Step 4: Segmentation (Optional)

Decide if you want to use K-Means clustering to segment your data. Simply choose the number of segments (clusters) you want to find, and the app will add a new "Segment" column to your dataset.

### Step 5: Build Your Dashboard

This is the final and most creative step.

- Use the **sidebar** to configure your dashboard.
- Select measures to display as **KPI Cards**.
- Choose a chart type, select the data for its axes, and click "**Add Chart**".
- Use the **Storytelling Assistant** to get suggestions on how to best order your charts for a compelling narrative.
- Customize colors, themes, and background.
- When you're ready, click the "Present 📽️" button to enter a clean, full-screen presentation mode.

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Manipulation**: Pandas, NumPy
- **Data Cleaning**: PyJanitor
- **Machine Learning & Analysis**: Scikit-learn, Featuretools
- **Data Visualization**: Plotly


## 👤 Author

**Aseem Mehrotra**

```mermaid
graph TD
    A[Start: Welcome Page] --> B{1. Upload CSV}
    B --> C[Automated Processing]
    C --> D{Data Cleaning}
    C --> E{Feature Engineering}
    C --> F{Advanced Analysis}
    D --> G[Profiling Report]
    E --> G
    F --> G
    G --> H["Manual Feature Creation (Optional)"]
    H --> I["Segmentation (Optional)"]
    I --> J[6. Build Dashboard]
    J --> K{Add KPI Cards}
    J --> L{Add Charts}
    J --> M{Customize Layout & Theme}
    J --> N{Use Storytelling Assistant}
    K --> O[End: Interactive & Presentation-Ready Dashboard]
    L --> O
    M --> O
    N --> O

    %% Styling
    style A fill:#268bd2,stroke:#333,stroke-width:2px,color:#fff
    style B fill:#6c71c4,stroke:#333,stroke-width:2px,color:#fff
    style C fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style D fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style E fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style F fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style G fill:#b58900,stroke:#333,stroke-width:2px,color:#fff
    style H fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style I fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style J fill:#d33682,stroke:#333,stroke-width:2px,color:#fff
    style K fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style L fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style M fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style N fill:#93a1a1,stroke:#333,stroke-width:2px,color:#fff
    style O fill:#2aa198,stroke:#333,stroke-width:2px,color:#fff




