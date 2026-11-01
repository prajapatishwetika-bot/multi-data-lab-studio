import io
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="DataLab Studio - BI Dashboard", page_icon="📊", layout="wide"
)

# --- Custom CSS for Card Grid & Gradient Background ---
st.markdown(
    """
    <style>
    .stApp {
        background: #000000;
     background-attachment: fixed;
     color: #FFFFFF;
    }
    
    /* Transform Streamlit buttons into gorgeous white cards */
    div.stButton > button {
        background-color: #black;
        color: #0f172a;
        border-radius: 16px;
        padding: 30px 20px;
        height: 140px;
        width: 100%;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.08), 0 8px 10px -6px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.8);
        font-weight: 600;
        font-size: 18px;
        transition: all 0.3s ease;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
    }

    div.stButton > button:hover {
        transform: translateY(-6px);
        box-shadow: 0 20px 30px -10px rgba(14, 165, 233, 0.3);
        border-color: #0ea5e9;
        background-color: #f8fafc;
        color: #0284c7;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 Multi-Functional Data Analysis & BI Dashboard Studio")
st.markdown(
    "Upload your dataset or paste raw data from the web to explore, clean,"
    " visualize, and analyze with built-in Power BI-style dashboards."
)

# --- 1. DATA INPUT (Upload or Paste) ---
st.sidebar.header("📁 1. Data Source")
input_method = st.sidebar.radio(
    "Choose input method:", ["Upload CSV/Excel", "Paste Raw Data (CSV format)"]
)

@st.cache_data
def load_data_from_buffer(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    else:
        return pd.read_excel(uploaded_file)

df = None

if input_method == "Upload CSV/Excel":
    uploaded_file = st.sidebar.file_uploader(
        "Upload your file", type=["csv", "xlsx"]
    )
    if uploaded_file is not None:
        try:
            df = load_data_from_buffer(uploaded_file)
        except Exception as e:
            st.error(f"Error loading file: {e}")
else:
    raw_data = st.sidebar.text_area(
        "Paste CSV data here (with headers):",
        height=150,
        placeholder=(
            "col1,col2,col3\nval1,val2,val3\nval4,val5,val6\n...or tab-separated"
            " text"
        ),
    )
    if raw_data:
        try:
            df = pd.read_csv(io.StringIO(raw_data))
            if df.shape[1] <= 1:
                df = pd.read_csv(io.StringIO(raw_data), sep="\t")
        except Exception as e:
            st.error(f"Could not parse pasted data: {e}")

if df is not None:
    # Working copy session state check
    if "df_cleaned" not in st.session_state:
        st.session_state["df_cleaned"] = df.copy()

    current_df = st.session_state["df_cleaned"]

    # --- Session State Navigation Tracker ---
    if "active_section" not in st.session_state:
        st.session_state["active_section"] = "Home Menu"

    # Home Menu / Card Grid View
    if st.session_state["active_section"] == "Home Menu":
        st.markdown("### 🧭 Choose an Analysis Module")
        st.markdown("Select any card below to launch the respective dashboard tool:")
        st.markdown("<br>", unsafe_allow_html=True)

        # Create a 3-column grid for cards
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("📋\n\nDataset Overview", use_container_width=True):
                st.session_state["active_section"] = "Dataset Overview"
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📈\n\nData Visualisation", use_container_width=True):
                st.session_state["active_section"] = "Data Visualisation"
                st.rerun()

        with col2:
            if st.button("🔍\n\nData Information", use_container_width=True):
                st.session_state["active_section"] = "Data Information"
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("📊\n\nPower BI Dashboard", use_container_width=True):
                st.session_state["active_section"] = "Power BI Dashboard"
                st.rerun()

        with col3:
            if st.button("🧹\n\nData Cleaning", use_container_width=True):
                st.session_state["active_section"] = "Data Cleaning"
                st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🖥️\n\nInteractive GUI", use_container_width=True):
                st.session_state["active_section"] = "Interactive GUI"
                st.rerun()

    else:
        # Back button to return to the card grid menu
        if st.button("⬅️ Back to Dashboard Menu"):
            st.session_state["active_section"] = "Home Menu"
            st.rerun()

        st.markdown("---")
        app_mode = st.session_state["active_section"]

        # --- 3. DATASET OVERVIEW ---
        if app_mode == "Dataset Overview":
            st.header("📋 3. Dataset Overview")

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Rows", f"{current_df.shape[0]:,}")
            col2.metric("Total Columns", current_df.shape[1])
            col3.metric(
                "Total Missing Values", f"{int(current_df.isna().sum().sum()):,}"
            )
            col4.metric(
                "Memory Usage",
                f"{current_df.memory_usage(deep=True).sum() / 1024 ** 2:.2f} MB",
            )

            st.markdown("---")
            st.subheader("Raw Data Preview")

            total_rows = len(current_df)
            default_rows = min(50, total_rows)

            view_option = st.radio(
                "Display Mode:",
                ["First N Rows", "Pagination / Chunk View"],
                horizontal=True,
            )

            if view_option == "First N Rows":
                rows_to_show = st.slider(
                    "Select number of rows to display",
                    min_value=5,
                    max_value=total_rows,
                    value=default_rows,
                    step=50 if total_rows > 500 else 5,
                )
                st.dataframe(current_df.head(rows_to_show), width="stretch")
            else:
                rows_per_page = st.selectbox(
                    "Rows per page", [25, 50, 100, 500], index=1
                )
                total_pages = max(
                    1,
                    (total_rows // rows_per_page)
                    + (1 if total_rows % rows_per_page > 0 else 0),
                )

                page_num = st.number_input(
                    "Page Number", min_value=1, max_value=total_pages, value=1
                )
                start_idx = (page_num - 1) * rows_per_page
                end_idx = min(start_idx + rows_per_page, total_rows)

                st.info(f"Showing rows {start_idx + 1} to {end_idx} of {total_rows}")
                st.dataframe(current_df.iloc[start_idx:end_idx], width="stretch")

            st.subheader("Dataset Summary Statistics")
            st.dataframe(current_df.describe(), width="stretch")

        # --- 4. DATA INFORMATION ---
        elif app_mode == "Data Information":
            st.header("🔍 4. Data Information & Structure")

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Column Data Types")
                dtypes_df = pd.DataFrame(
                    {
                        "Column": current_df.columns,
                        "Data Type": current_df.dtypes.astype(str),
                        "Non-Null Count": current_df.notnull().sum(),
                    }
                )
                st.dataframe(dtypes_df, width="stretch")

            with col2:
                st.subheader("Missing Values per Column")
                missing_df = pd.DataFrame(
                    {
                        "Missing Count": current_df.isna().sum(),
                        "Percentage (%)": (
                            current_df.isna().mean() * 100
                        ).round(2),
                    }
                )
                st.dataframe(missing_df, width="stretch")

            st.subheader("Unique Value Counts")
            unique_counts = pd.DataFrame(
                {
                    "Column": current_df.columns,
                    "Unique Values": [
                        current_df[col].nunique() for col in current_df.columns
                    ],
                }
            )
            st.dataframe(unique_counts, width="stretch")

        # --- 5. DATA CLEANING ---
        elif app_mode == "Data Cleaning":
            st.header("🧹 5. Data Cleaning Operations")
            st.markdown(
                "Apply cleaning steps dynamically. Changes will reflect in subsequent sections."
            )

            if st.button("Reset to Original Data"):
                st.session_state["df_cleaned"] = df.copy()
                st.success("Dataset reset to original!")
                st.rerun()

            cleaning_option = st.selectbox(
                "Select Cleaning Operation",
                [
                    "Drop Rows with Missing Values",
                    "Fill Missing Values (Numeric)",
                    "Drop Duplicate Rows",
                    "Drop Specific Columns",
                ],
            )

            if cleaning_option == "Drop Rows with Missing Values":
                if st.button("Apply Drop NA"):
                    st.session_state["df_cleaned"] = current_df.dropna()
                    st.success("Rows with missing values dropped successfully!")
                    st.rerun()

            elif cleaning_option == "Fill Missing Values (Numeric)":
                fill_method = st.selectbox(
                    "Fill strategy", ["Mean", "Median", "Constant (0)"]
                )
                numeric_cols = current_df.select_dtypes(
                    include=np.number
                ).columns.tolist()

                if st.button("Apply Imputation"):
                    temp_df = current_df.copy()
                    for col in numeric_cols:
                        if fill_method == "Mean":
                            temp_df[col] = temp_df[col].fillna(temp_df[col].mean())
                        elif fill_method == "Median":
                            temp_df[col] = temp_df[col].fillna(temp_df[col].median())
                        elif fill_method == "Constant (0)":
                            temp_df[col] = temp_df[col].fillna(0)
                    st.session_state["df_cleaned"] = temp_df
                    st.success(f"Missing values filled using {fill_method}!")
                    st.rerun()

            elif cleaning_option == "Drop Duplicate Rows":
                before_count = len(current_df)
                if st.button("Remove Duplicates"):
                    st.session_state["df_cleaned"] = current_df.drop_duplicates()
                    after_count = len(st.session_state["df_cleaned"])
                    st.success(f"Removed {before_count - after_count} duplicate rows.")
                    st.rerun()

            elif cleaning_option == "Drop Specific Columns":
                cols_to_drop = st.multiselect(
                    "Select columns to drop", current_df.columns.tolist()
                )
                if st.button("Drop Selected Columns") and cols_to_drop:
                    st.session_state["df_cleaned"] = current_df.drop(
                        columns=cols_to_drop
                    )
                    st.success(f"Dropped columns: {', '.join(cols_to_drop)}")
                    st.rerun()

            st.subheader("Current Cleaned Data Preview")
            st.dataframe(current_df.head(10), width="stretch")

        # --- 6. DATA VISUALISATION ---
        elif app_mode == "Data Visualisation":
            st.header("📈 6. Data Visualisation Suite")

            numeric_cols = current_df.select_dtypes(
                include=np.number
            ).columns.tolist()
            categorical_cols = current_df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

            viz_type = st.selectbox(
                "Select Chart Type",
                [
                    "Scatter Plot",
                    "Histogram / Distribution",
                    "Box Plot",
                    "Count Plot",
                    "Correlation Heatmap",
                ],
            )

            fig, ax = plt.subplots(figsize=(10, 5))

            if viz_type == "Scatter Plot":
                if len(numeric_cols) >= 2:
                    x_axis = st.selectbox("X-axis", numeric_cols, index=0)
                    y_axis = st.selectbox("Y-axis", numeric_cols, index=1)
                    hue_col = (
                        st.selectbox("Hue (Categorical)", ["None"] + categorical_cols)
                        if categorical_cols
                        else "None"
                    )

                    if hue_col != "None":
                        sns.scatterplot(
                            data=current_df, x=x_axis, y=y_axis, hue=hue_col, ax=ax
                        )
                    else:
                        sns.scatterplot(data=current_df, x=x_axis, y=y_axis, ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning("Need at least 2 numeric columns for a scatter plot.")

            elif viz_type == "Histogram / Distribution":
                if numeric_cols:
                    col = st.selectbox("Select Numeric Column", numeric_cols)
                    bins = st.slider("Number of Bins", 5, 100, 20)
                    sns.histplot(
                        current_df[col], bins=bins, kde=True, ax=ax, color="skyblue"
                    )
                    ax.set_title(f"Distribution of {col}")
                    st.pyplot(fig)
                else:
                    st.warning("No numeric columns available.")

            elif viz_type == "Box Plot":
                if numeric_cols:
                    y_col = st.selectbox("Numeric Value (Y-axis)", numeric_cols)
                    x_col = (
                        st.selectbox(
                            "Group By (Categorical X-axis)", ["None"] + categorical_cols
                        )
                        if categorical_cols
                        else "None"
                    )

                    if x_col != "None":
                        sns.boxplot(data=current_df, x=x_col, y=y_col, ax=ax, palette="Set2")
                        plt.xticks(rotation=45)
                    else:
                        sns.boxplot(y=current_df[y_col], ax=ax, color="orange")
                    st.pyplot(fig)
                else:
                    st.warning("Need numeric columns for box plots.")

            elif viz_type == "Count Plot":
                if categorical_cols:
                    cat_col = st.selectbox("Select Categorical Column", categorical_cols)
                    sns.countplot(
                        data=current_df,
                        x=cat_col,
                        order=current_df[cat_col].value_counts().index[:10],
                        ax=ax,
                        palette="viridis",
                    )
                    plt.xticks(rotation=45)
                    st.pyplot(fig)
                else:
                    st.warning("No categorical columns available.")

            elif viz_type == "Correlation Heatmap":
                if len(numeric_cols) >= 2:
                    corr = current_df[numeric_cols].corr()
                    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
                    st.pyplot(fig)
                else:
                    st.warning(
                        "Need at least 2 numeric columns for correlation calculation."
                    )

        # --- 7. POWER BI STYLE DASHBOARD ---
        elif app_mode == "Power BI Dashboard":
            st.header("📊 7. Power BI Executive Dashboard")
            st.markdown(
                "Interactive executive dashboard layout featuring KPI summary cards,"
                " bar graphs, and pie/donut charts."
            )

            numeric_cols = current_df.select_dtypes(
                include=np.number
            ).columns.tolist()
            categorical_cols = current_df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()

            if numeric_cols:
                kpi1, kpi2, kpi3 = st.columns(3)
                primary_metric = numeric_cols[0]
                kpi1.metric(
                    label=f"Total Records", value=f"{len(current_df):,}"
                )
                kpi2.metric(
                    label=f"Sum of {primary_metric}",
                    value=f"{current_df[primary_metric].sum():,.2f}",
                )
                kpi3.metric(
                    label=f"Average {primary_metric}",
                    value=f"{current_df[primary_metric].mean():,.2f}",
                )
                st.markdown("---")

            col_a, col_b = st.columns(2)

            with col_a:
                st.subheader("📊 Bar / Column Graph")
                if categorical_cols and numeric_cols:
                    bar_x = st.selectbox(
                        "Category Dimension (X-axis)", categorical_cols, key="pbi_bar_x"
                    )
                    bar_y = st.selectbox(
                        "Numeric Measure (Y-axis)", numeric_cols, key="pbi_bar_y"
                    )

                    agg_df = (
                        current_df.groupby(bar_x)[bar_y]
                        .sum()
                        .reset_index()
                        .sort_values(by=bar_y, ascending=False)
                        .head(10)
                    )
                    fig_bar = px.bar(
                        agg_df,
                        x=bar_x,
                        y=bar_y,
                        title=f"Top 10 {bar_x} by {bar_y}",
                        color=bar_y,
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_bar, width="stretch")
                else:
                    st.warning(
                        "Dataset requires both categorical and numeric columns for bar charts."
                    )

            with col_b:
                st.subheader("🥧 Pie / Donut Chart")
                if categorical_cols:
                    pie_col = st.selectbox(
                        "Category for Distribution", categorical_cols, key="pbi_pie_col"
                    )
                    pie_data = current_df[pie_col].value_counts().reset_index()
                    pie_data.columns = [pie_col, "Count"]
                    pie_data = pie_data.head(8)

                    fig_pie = px.pie(
                        pie_data,
                        names=pie_col,
                        values="Count",
                        title=f"Share Distribution by {pie_col}",
                        hole=0.4,
                        template="plotly_white",
                    )
                    st.plotly_chart(fig_pie, width="stretch")
                else:
                    st.warning("No categorical columns available for pie chart.")

        # --- 8. INTERACTIVE GUI ---
        elif app_mode == "Interactive GUI":
            st.header("🖥️ 8. Interactive Data GUI & Query Tool")
            st.markdown(
                "Use dynamic filters and search parameters to query your dataset instantly."
            )

            st.sidebar.markdown("---")
            st.sidebar.subheader("🔎 GUI Filters")

            filtered_df = current_df.copy()

            categorical_cols = current_df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()
            numeric_cols = current_df.select_dtypes(
                include=np.number
            ).columns.tolist()

            for col in categorical_cols[:3]:
                unique_vals = current_df[col].dropna().unique().tolist()
                if len(unique_vals) < 50:
                    selected_vals = st.sidebar.multiselect(
                        f"Filter {col}", unique_vals, default=[]
                    )
                    if selected_vals:
                        filtered_df = filtered_df[filtered_df[col].isin(selected_vals)]

            for col in numeric_cols[:2]:
                min_val = float(current_df[col].min())
                max_val = float(current_df[col].max())
                if min_val != max_val:
                    slider_vals = st.sidebar.slider(
                        f"Range for {col}", min_val, max_val, (min_val, max_val)
                    )
                    filtered_df = filtered_df[
                        (filtered_df[col] >= slider_vals[0])
                        & (filtered_df[col] <= slider_vals[1])
                    ]

            st.subheader(
                f"Filtered Results ({len(filtered_df)} of {len(current_df)} rows matching criteria)"
            )
            st.dataframe(filtered_df, width="stretch")

            filtered_csv = filtered_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                "📥 Download Filtered Data Subset",
                filtered_csv,
                "filtered_data.csv",
                "text/csv",
            )

else:
    st.info(
        "👈 Please upload a file or paste raw CSV data from the sidebar to start exploring!"
    )
