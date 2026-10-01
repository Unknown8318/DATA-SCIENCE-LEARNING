# modules/exercises/streamlit/app.py

# =============================================================================
# 1. IMPORTS & DASHBOARD CONFIGURATION
# =============================================================================
# Streamlit provides the web components, state management, and server engine.
import streamlit as st

# Pandas handles tabular data loading, filtering, and transformation.
import pandas as pd

# Page config sets browser tab title, favicon, and expands the layout to full screen width.
# NOTE: st.set_page_config() must always be the very first Streamlit call in your script.
st.set_page_config(page_title="Telemetry & Log Filter", layout="wide")

# Static markdown headers to set up the dashboard UI
st.title("🛡️ Security & Asset Log Analyzer")
st.markdown("Upload telemetry or event logs (`.csv`) to filter and inspect records interactively.")


# =============================================================================
# 2. DATA INGESTION (UPLOAD OR FALLBACK)
# =============================================================================
# st.file_uploader creates a file drop-zone that accepts files from the client.
# It returns a file-like object in memory, or None if nothing has been selected yet.
uploaded_file = st.file_uploader("Upload CSV Log File", type=["csv"])

if uploaded_file is not None:
    # If the user uploads a CSV, read that byte stream directly into a pandas DataFrame.
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded '{uploaded_file.name}' ({len(df)} rows)")
else:
    # If no file is provided, supply a fallback dataset so the UI stays functional.
    st.info("No file uploaded. Displaying default mock telemetry records.")
    
    mock_data = {
        "timestamp": [
            "2026-10-01 08:12:00", 
            "2026-10-01 08:14:22", 
            "2026-10-01 08:15:05", 
            "2026-10-01 08:21:40", 
            "2026-10-01 08:33:15"
        ],
        "asset_id": ["SRV-01", "FW-EDGE", "SRV-02", "WS-104", "FW-EDGE"],
        "severity": ["INFO", "WARNING", "CRITICAL", "INFO", "CRITICAL"],
        "event_code": [100, 401, 500, 100, 502],
        "message": [
            "Routine handshake", 
            "Unauthorized port scan probe", 
            "Service buffer overflow", 
            "User login success", 
            "DDoS signature threshold exceeded"
        ]
    }
    # Turn the Python dictionary into a structured 2D DataFrame table
    df = pd.DataFrame(mock_data)


# =============================================================================
# 3. SIDEBAR CONTROLS & DYNAMIC FILTERS
# =============================================================================
# st.sidebar places input widgets into a collapsible side navigation bar.
st.sidebar.header("🔍 Filter Records")

# Extract unique, non-null values from the 'severity' column to populate the dropdown.
# .dropna() removes missing values, and .unique() eliminates duplicate categories.
available_severities = df["severity"].dropna().unique().tolist()

# st.sidebar.multiselect lets users pick one or multiple values.
# 'default=available_severities' starts with all categories selected by default.
selected_severities = st.sidebar.multiselect(
    "Select Severity Level",
    options=available_severities,
    default=available_severities
)

# Text input box for free-text string searching.
# .strip() removes accidental leading/trailing spaces, and .lower() normalizes for case-insensitivity.
search_query = st.sidebar.text_input("Search Message Keyword", "").strip().lower()


# =============================================================================
# 4. PANDAS FILTERING ENGINE
# =============================================================================
# 1. Severity filter:
# df['severity'].isin(...) checks each row to see if its severity is inside the selected list.
# This produces a boolean True/False Series, which slices the DataFrame down to matching rows.
filtered_df = df[df["severity"].isin(selected_severities)]

# 2. Text keyword filter:
# If the user typed a keyword, perform a case-insensitive substring search across the 'message' column.
if search_query:
    filtered_df = filtered_df[filtered_df["message"].str.lower().str.contains(search_query)]


# =============================================================================
# 5. METRICS & KPI CARDS
# =============================================================================
# st.columns(3) splits the main display area horizontally into three equal columns.
col1, col2, col3 = st.columns(3)

# col.metric displays a clean card with a title and a prominent number.
col1.metric("Total Records", len(df))
col2.metric("Matching Filter", len(filtered_df))

# Count how many critical rows survived the active filter criteria.
critical_count = len(filtered_df[filtered_df["severity"] == "CRITICAL"])
col3.metric("Critical Alerts", critical_count)

# Visual separator line between summary KPIs and the data table
st.divider()


# =============================================================================
# 6. TABULAR DISPLAY & EXPORT
# =============================================================================
st.subheader("Filtered Log Entries")

# st.dataframe displays the table in an interactive viewer (sortable, searchable, resizable columns).
# use_container_width=True stretches the table to fill the entire horizontal width.
st.dataframe(filtered_df, use_container_width=True)

# Convert the filtered DataFrame slice into CSV format in memory (encoded as UTF-8 bytes).
csv_export = filtered_df.to_csv(index=False).encode("utf-8")

# st.download_button triggers a direct browser file download for the user.
st.download_button(
    label="📥 Download Filtered Results as CSV",
    data=csv_export,
    file_name="filtered_telemetry.csv",
    mime="text/csv"
)