## Data Exploration & Visualization Through Titanic Dataset (https://www.kaggle.com/competitions/titanic/data)

# =============================================================================
# 1. IMPORTS & DASHBOARD CONFIGURATION
# =============================================================================

import streamlit as st # Streamlit provides the web components, state management, and server engine.
import pandas as pd # Pandas handles tabular data loading, filtering, and transformation.
import matplotlib.pyplot as plt  # Low-level control, subplots, exact layout design
import seaborn as sns # Statistical aggregations, built-in themes, distributions
import plotly, nbformat #High-performance interactive tooltips, zooming, HTML export
import pathlib #object-oriented approach to handling filesystem paths

# Page config sets browser tab title, favicon, and expands the layout to full screen width.
# NOTE: st.set_page_config() must always be the very first Streamlit call in your script.
st.set_page_config(page_title="Titanic Analytics and", layout="wide")

# Static markdown headers to set up the dashboard UI
st.title("Titanic Disaster: Exploratory Data Analysis")
st.markdown("Explore demographics, passenger fares, and survival factors interactively.")
uploaded_file = st.file_uploader("Upload Titanic CSV File", type=["csv"])

# =============================================================================
# 2. DATA INGESTION (UPLOAD OR FALLBACK)
# =============================================================================
data_dir = pathlib.Path(__file__).parent / "data"
default_data= data_dir / "train.csv"

@st.cache_data #Decorator to cache functions that return data (e.g. dataframe transforms, database queries, ML inference).
def load_default_data(filepath: pathlib.Path) -> pd.DataFrame:
    if filepath.exists():
        return pd.read_csv(filepath)
    return pd.DataFrame()

if uploaded_file is not None:
    # If the user uploads a CSV, read that byte stream directly into a pandas DataFrame.
    df = pd.read_csv(uploaded_file)
    st.success(f"Loaded '{uploaded_file.name}' ({len(df)} rows)")
else:
    df = load_default_data(default_data)
    if not df.empty:
        st.sidebar.info("Using baseline dataset.")
    else:
        st.error(
            f'Default dataset not found at "{default_data}". Please place "train.csv" in "data/" or upload a file.'
        )
        st.stop()
# =============================================================================
#  3. DOWNLOAD BUTTON 
# =============================================================================

# Convert the current dataframe to CSV for user export
csv_buffer = df.to_csv(index=False).encode("utf-8")

st.sidebar.download_button(
    label="📥 Download Current Data (CSV)",
    data=csv_buffer,
    file_name="titanic_export.csv",
    mime="text/csv",
)   

# =============================================================================
# 4. DISPLAY BASELINE DATA & WORKFLOW TABS
# =============================================================================
st.subheader("Raw Dataset Preview")
st.dataframe(df.head(20), use_container_width=True)

tab_audit, tab_clean, tab_stats, tab_viz = st.tabs([
    "🔍 Step 1: Missing Data Audit",
    "🧹 Step 2: Data Cleaning",
    "📊 Step 3: Summary Statistics",
    "📈 Step 4: Visualizations",
])
# =============================================================================
# 5. Data Exploration & Missing Value Audit
# =============================================================================

with tab_audit:
    st.subheader("Missing Data Audit")
    st.dataframe(df.head(20), use_container_width=(True))

    missing_data = df.isnull().sum() #counting the missing values per column

    filter_column = missing_data[missing_data > 0] #filter to only colums that have at least 1 missing value

    sorting_column = filter_column.sort_values(ascending = False)

    st.write("Columns with missing entries: ")
    st.dataframe(sorting_column)

# =============================================================================
# 6. Strategizing Mising Data & Data Cleaning Pipeline
# Columns Missing Data: Cabin = 687, Age = 177, & Embarked = 2
# =============================================================================
with tab_clean:
    # Concept: What is the "Mode"?
    #   Mean: The arithmetic average (only works on numbers).
    #   Median: The middle value when sorted (only works on numbers).
    #   Mode: The most frequent value (works on text and categories).
    st.subheader("Strategizing Mising Data & Data Cleaning Pipeline")

    # C = Cherbourg, Q = Queenstown, and S = Southampton 
    # ======================= Embarked =========================
    # 2 missing out of 891 rows, or ~0.2% missing

    st.subheader("The Embarked",divider = True)
    #Coverting the S, C, and Q to the actual port name = easier to read. much nice. much wow
    port_mapping = {
        'S': "Southampton",
        'C': "Cherbourg",
        'Q': 'Queenstown'
        }

    df["Embarked"] = df["Embarked"].map(port_mapping) #.map() is a cleaner, efficient, and consistent method to find and replace items. 

    most_common_port = df["Embarked"].mode()[0]
    st.write(f"The most frequently used port to board the Titanic was: {most_common_port}")

    df["Embarked"] = df["Embarked"].fillna(most_common_port) #filling the missing blanks with the most common port

    st.write(f"Missing Embarked values left: {df['Embarked'].isnull().sum()}")

    # ======================= Age =========================
    # 177 missing out of 891 rows, or ~20% missing
    st.subheader("Age Imputation Strategy",divider = True)

    grouped_median = df.groupby(["Pclass", "Sex"])["Age"].median() # calculating median age group by class and sex

    st.write(f"The Median age by Passenger class and Sex:" )
    st.dataframe(grouped_median)

    df["Age"] = df.groupby(["Pclass", "Sex"])["Age"].transform(
        lambda group:group.fillna(group.median())
    )

    st.write(f"Missing Age values left: {df['Age'].isnull().sum()}")


    # ======================= Cabin =========================
    # 687 missing out of 891 rows, or ~77% missing
    # Due to sheer number missing information, this is going to be a bit more intense and because this we don't want to fabricate information
    # If someone had a cabin room number it typically meant they were either wealthy or not wealthy
    # We are going to record this in a binary strategy 1s and 0s. 1 = recorded cabin | 0 = not recorded

    st.subheader("The Cabin Records, to be or not..",divider = True)

    df["Has_Cabin"] = df["Cabin"].notna().astype(int) #converting our data or missing data to true and false

    df["Deck"] = df["Cabin"].dropna().astype(str).str[0] #the .str[0] is looking at the first character in the string
    df["Deck"] = df["Cabin"].fillna("Unknown") # converting our nan to unknown

    cabin_survival = df.groupby("Has_Cabin")["Survived"].mean()
    st.write(f"The Survival rate by record status (0 = No Cabin, 1 = Has Cabin)")
    st.dataframe(cabin_survival)

    # ======================= Final Audit =========================

    df = df.drop(columns=["Cabin"])

    st.subheader("Post-Cleaning Verification", divider=True)

    remaining_nulls = df.isnull().sum()

    st.write("Columns with missing values:")
    st.dataframe(remaining_nulls)

    if remaining_nulls.sum() == 0:
        st.success("Dataset is clean. No Missing Values")


# =============================================================================
# 7. Descriptive Summary Statistics
# =============================================================================

with tab_stats:
    st.subheader("Descriptive Summary Statistics")

    num_summary = df.describe().round(2)
    st.write("The Numerical Features Summary: ")
    st.dataframe(num_summary)

    #Each row provides a specific metric:
        # What is the center of the data? (mean, median)
            # count: Total non-null values.
            # mean: The arithmetic average.
        # How spread out is the data? (standard deviation, minimum, maximum, percentiles)
            # std: Standard deviation (spread of data around the mean).
            # min / max: Lower and upper boundaries.
            # 25%, 50%, 75%: Percentiles (the 50% percentile is the median).
    
    cat_summary = df.describe(include=['O'])
    st.write("Categorical Features Summary: ")
    st.dataframe(cat_summary)

    st.markdown("### Survival Rate by Gender (%)")
    gender_survival = df.groupby ("Sex")["Survived"].mean().to_frame()
    st.dataframe(gender_survival.style.format("{:.1%}"))
    
    st.markdown("### Survival Rate by Ticket Class (%)")
    class_survival = df.groupby ("Pclass")["Survived"].mean().to_frame()
    st.dataframe(class_survival.style.format("{:.1%}"))

    st.markdown("### Survival Matrix: Class vs. Gender (%)")
    survival_matrix = pd.crosstab(df["Pclass"], df["Sex"], values=df["Survived"], aggfunc="mean").round(3)
    st.dataframe(survival_matrix.style.format("{:.1%}"))

# =============================================================================
# 7. Visualization of Dataset
# =============================================================================

with tab_viz:
    st.subheader("Visual Exploration Across Python Libraries")

    #Sub-tabbing
    subtab_mpl, subtab_sns, subtab_plotly = st.tabs(
        ["📈 Matplotlib", "🎨 Seaborn", "⚡ Plotly Express"]
    )
    with subtab_mpl:
        st.markdown("### Chart 1: Passenger Distribution")
        
        fig, ax = plt.subplots(figsize=(8, 4))

        ax.hist(
            df["Age"],
            bins=20,
            color="#1f77b4",
            linewidth=1.2,
            alpha=0.85,
        )
        ax.set_title("Age Distribution of Passengers", fontsize=12, fontweight = "bold")
        ax.set_xlabel("Age (years)")
        ax.set_ylabel("Passenger Count")
        ax.grid(axis="y", linestyle="--", alpha=0.5)

        st.pyplot(fig)