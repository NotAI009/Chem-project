import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AQI Analysis - Chemistry Project",
    layout="wide",
    page_icon="🌫️",
)

# -------------------------------------------------
# BASIC STYLING
# -------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #050816;
        color: #eaeaea;
        font-family: 'Segoe UI', sans-serif;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    h1, h2, h3, h4 {
        color: #e2e8f0;
    }
    .metric-card {
        padding: 1rem 1.2rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.9);
        border: 1px solid rgba(148, 163, 184, 0.3);
        box-shadow: 0 10px 30px rgba(0,0,0,0.35);
    }
    .chem-card {
        padding: 1rem 1.2rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(56, 189, 248, 0.6);
        box-shadow: 0 8px 24px rgba(8,47,73,0.8);
    }
    .good-chip {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background: #16a34a22;
        border: 1px solid #16a34a;
        font-size: 0.8rem;
    }
    .moderate-chip {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background: #eab30822;
        border: 1px solid #eab308;
        font-size: 0.8rem;
    }
    .poor-chip {
        display: inline-block;
        padding: 0.2rem 0.6rem;
        border-radius: 999px;
        background: #ef444422;
        border: 1px solid #ef4444;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------
# CHEMISTRY INFO
# -------------------------------------------------
pollutant_info = {
    "PM2_5": {
        "name": "Particulate Matter 2.5",
        "formula": "Mixture (≤ 2.5 μm)",
        "type": "Primary & Secondary Pollutant",
        "sources": "Vehicle exhaust, biomass burning, industrial emissions, secondary formation from SO₂ & NOx.",
        "chemistry": (
            "PM2.5 often contains sulfates (from SO₂ oxidation), nitrates (from NOx), "
            "organic carbon and metals. Due to very small size, it penetrates deep into lungs."
        ),
        "health": "Irritates lungs, reduces gas exchange, increases risk of asthma, bronchitis, and cardiovascular diseases."
    },
    "PM10": {
        "name": "Particulate Matter 10",
        "formula": "Mixture (≤ 10 μm)",
        "type": "Primary Pollutant",
        "sources": "Dust, construction activities, road resuspension, burning of fuels.",
        "chemistry": (
            "Coarse particles with dust, soil, metals, carbonaceous material. "
            "Less deep penetration than PM2.5 but still harmful."
        ),
        "health": "Irritation of eyes, nose, throat; respiratory problems."
    },
    "NO2": {
        "name": "Nitrogen Dioxide",
        "formula": "NO₂",
        "type": "Primary & Secondary Pollutant",
        "sources": "High-temperature combustion in vehicles, power plants, industries.",
        "chemistry": (
            "NO₂ participates in photochemical smog. Under sunlight it forms NO and atomic oxygen, "
            "which leads to O₃ formation.\n\n"
            "NO₂ + hν → NO + O·\nO· + O₂ → O₃\n"
        ),
        "health": "Irritates respiratory tract, reduces lung function, aggravates asthma."
    },
    "SO2": {
        "name": "Sulfur Dioxide",
        "formula": "SO₂",
        "type": "Primary Pollutant",
        "sources": "Burning coal and oil containing sulfur, smelters.",
        "chemistry": (
            "SO₂ oxidizes in atmosphere to SO₃, which forms sulfuric acid.\n\n"
            "2 SO₂ + O₂ → 2 SO₃\nSO₃ + H₂O → H₂SO₄\n\n"
            "This contributes to acid rain."
        ),
        "health": "Causes irritation in eyes, nose, throat; leads to breathing difficulty; damages plants."
    },
    "O3": {
        "name": "Ozone (tropospheric)",
        "formula": "O₃",
        "type": "Secondary Pollutant",
        "sources": "Formed in atmosphere from NOx and volatile organic compounds (VOCs) under sunlight.",
        "chemistry": (
            "Key component of photochemical smog. Formed by reactions involving NO₂, O₂ and sunlight, "
            "and further reactions with VOCs."
        ),
        "health": "Strong oxidizing agent; damages lung tissue, causes chest pain & coughing."
    },
    "CO": {
        "name": "Carbon Monoxide",
        "formula": "CO",
        "type": "Primary Pollutant",
        "sources": "Incomplete combustion of carbon-based fuels (vehicles, stoves, generators).",
        "chemistry": (
            "Binds strongly with hemoglobin to form carboxyhemoglobin, reducing oxygen transport in blood."
        ),
        "health": "Reduces oxygen supply to body, causes headache, dizziness; at high levels can be fatal."
    },
}

# -------------------------------------------------
# SIDEBAR – DATA LOADING
# -------------------------------------------------
st.sidebar.title("⚙️ Controls")

uploaded_file = st.sidebar.file_uploader(
    "Upload AQI CSV file (optional)",
    type=["csv"],
    help="If you don't upload, the app will use aqi_data_180_days.csv from the project folder."
)

# Load data: uploaded file > local CSV > None
df = None

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
else:
    try:
        df = pd.read_csv("aqi_data_180_days.csv")
    except FileNotFoundError:
        df = None

if df is not None and "date" in df.columns:
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

# -------------------------------------------------
# HEADER
# -------------------------------------------------
st.title("🌫️ AQI Analysis Dashboard – Chemistry Perspective")

st.markdown(
    """
    This project connects **data analysis** with **environmental chemistry**.

    We study how different air pollutants (PM₂.₅, PM₁₀, NO₂, SO₂, O₃, CO) affect the **Air Quality Index (AQI)**  
    and relate it to their **chemical nature, atmospheric reactions, and health effects**.
    """
)

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab_intro, tab_data, tab_analysis, tab_chem = st.tabs(
    ["📘 Theory & AQI Basics", "📊 Data View", "📈 AQI Analysis", "🧪 Chemistry of Pollutants"]
)

# -------------------------------------------------
# TAB 1: INTRO / THEORY
# -------------------------------------------------
with tab_intro:
    st.subheader("What is AQI?")

    st.markdown(
        """
        The **Air Quality Index (AQI)** is a numerical scale used to describe how clean or polluted 
        the air is, and what associated health effects might be a concern.

        It is calculated using concentrations of key pollutants, such as:
        - PM₂.₅ (fine particulate matter)
        - PM₁₀ (coarse particulate matter)
        - NO₂ (nitrogen dioxide)
        - SO₂ (sulfur dioxide)
        - O₃ (ozone)
        - CO (carbon monoxide)

        AQI values are generally interpreted as:
        - **0–50**: <span class="good-chip">Good</span> – Air quality is considered satisfactory.
        - **51–100**: <span class="moderate-chip">Moderate</span> – Acceptable but may cause minor issues for sensitive groups.
        - **101–200**: <span class="poor-chip">Unhealthy for sensitive groups</span>.
        - **201–300**: Very unhealthy.
        - **>300**: Hazardous.

        From a **chemistry** point of view, AQI is a way to quantify the effect of **gases and particles** formed by 
        combustion, oxidation, and atmospheric reactions.
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.subheader("Chemistry connection")
    st.markdown(
        """
        - **Combustion chemistry**: Burning fossil fuels produces CO, CO₂, NO, NO₂, SO₂, and particulate matter.  
        - **Oxidation in atmosphere**: Gases like SO₂ and NO₂ are oxidized to acids (H₂SO₄, HNO₃), contributing to **acid rain**.  
        - **Photochemical reactions**: Under sunlight, NO₂ and VOCs form **ozone (O₃)** and **photochemical smog**.  
        - **Particulate chemistry**: Sulfates, nitrates, and organic compounds condense to form PM₂.₅ and PM₁₀.

        This dashboard allows you to observe how changes in pollutant levels affect AQI over **time and city**, 
        and to relate that to these **chemical processes**.
        """
    )

# -------------------------------------------------
# TAB 2: DATA VIEW
# -------------------------------------------------
with tab_data:
    st.subheader("Dataset Overview")

    if df is None:
        st.warning("No data found. Upload a CSV or keep aqi_data_180_days.csv in the same folder as app.py.")
    else:
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            st.markdown("### Raw Data (first 20 rows)")
            st.dataframe(df.head(20), use_container_width=True)

        with col2:
            st.markdown("### Basic Info")
            st.markdown(f"**Total rows:** {len(df)}")
            if "city" in df.columns:
                st.markdown(f"**Cities:** {', '.join(sorted(df['city'].astype(str).unique()))}")
            if "date" in df.columns and df["date"].notna().any():
                st.markdown(f"**Start date:** {df['date'].min().date()}")
                st.markdown(f"**End date:** {df['date'].max().date()}")

        with col3:
            st.markdown("### Columns present")
            st.write(list(df.columns))

        st.markdown("---")
        st.markdown("### AQI Distribution")
        if "AQI" in df.columns:
            fig_hist = px.histogram(
                df,
                x="AQI",
                nbins=30,
                title="Distribution of AQI values",
            )
            fig_hist.update_layout(template="plotly_dark", height=400)
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.error("No 'AQI' column found in the dataset.")

# -------------------------------------------------
# TAB 3: AQI ANALYSIS
# -------------------------------------------------
with tab_analysis:
    st.subheader("Visual Analysis of AQI and Pollutants")

    if df is None:
        st.warning("Upload a CSV file or place aqi_data_180_days.csv in the project folder.")
    else:
        if "city" not in df.columns:
            st.error("The dataset must contain a 'city' column.")
        else:
            # Filters
            cities = sorted(df["city"].astype(str).unique())
            selected_city = st.selectbox("Select City", cities)

            df_city = df[df["city"] == selected_city].copy()

            if "date" in df_city.columns and df_city["date"].notna().any():
                df_city = df_city.sort_values("date")
                min_date = df_city["date"].min()
                max_date = df_city["date"].max()
                start_date, end_date = st.slider(
                    "Select Date Range",
                    min_value=min_date.to_pydatetime(),
                    max_value=max_date.to_pydatetime(),
                    value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
                )
                mask = (df_city["date"] >= pd.to_datetime(start_date)) & (df_city["date"] <= pd.to_datetime(end_date))
                df_city = df_city[mask]

            # Summary metrics
            st.markdown("### City AQI Summary")
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Average AQI", f"{df_city['AQI'].mean():.1f}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_b:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Max AQI", f"{df_city['AQI'].max():.0f}")
                st.markdown("</div>", unsafe_allow_html=True)
            with col_c:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.metric("Min AQI", f"{df_city['AQI'].min():.0f}")
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("---")

            # Time series AQI
            if "date" in df_city.columns and df_city["date"].notna().any():
                fig_ts = px.line(
                    df_city,
                    x="date",
                    y="AQI",
                    title=f"AQI over time – {selected_city}",
                    markers=True,
                )
                fig_ts.update_layout(template="plotly_dark", height=420)
                st.plotly_chart(fig_ts, use_container_width=True)

            # Correlation heatmap
            pollutant_cols = [col for col in ["PM2_5", "PM10", "NO2", "SO2", "O3", "CO", "AQI"] if col in df_city.columns]
            if len(pollutant_cols) > 2:
                st.markdown("### Correlation between AQI and Pollutants")
                corr = df_city[pollutant_cols].corr()

                fig_corr = px.imshow(
                    corr.values,
                    x=pollutant_cols,
                    y=pollutant_cols,
                    text_auto=".2f",
                    aspect="auto",
                    title="Correlation Matrix",
                )
                fig_corr.update_layout(template="plotly_dark", height=500)
                st.plotly_chart(fig_corr, use_container_width=True)

                st.markdown(
                    """
                    **Chemistry + Data Interpretation:**  
                    - High positive correlation between **PM₂.₅ / PM₁₀ and AQI** shows that particulate matter,
                      formed from combustion and gas-to-particle conversion (sulfates, nitrates), strongly worsens air quality.  
                    - Correlations with **NO₂** and **SO₂** relate to combustion sources and secondary particle formation.
                    """
                )

            # Individual pollutant vs AQI
            st.markdown("---")
            st.markdown("### Pollutant vs AQI (Scatter Plot)")

            pollutant_choices = [p for p in ["PM2_5", "PM10", "NO2", "SO2", "O3", "CO"] if p in df_city.columns]
            if pollutant_choices:
                selected_pollutant = st.selectbox("Select pollutant", pollutant_choices)
                fig_scatter = px.scatter(
                    df_city,
                    x=selected_pollutant,
                    y="AQI",
                    title=f"{selected_pollutant} vs AQI – {selected_city}",
                    trendline="ols",
                )
                fig_scatter.update_layout(template="plotly_dark", height=420)
                st.plotly_chart(fig_scatter, use_container_width=True)

                st.markdown(
                    f"""
                    - This graph shows how **{selected_pollutant} concentration** influences AQI.  
                    - The trendline gives an approximate **mathematical relation** between pollutant level and AQI.  
                    - Chemically, higher levels of this pollutant indicate more harmful **gaseous/particulate species** in the air,
                      leading to poorer air quality and health issues.
                    """
                )

# -------------------------------------------------
# TAB 4: CHEMISTRY OF POLLUTANTS
# -------------------------------------------------
with tab_chem:
    st.subheader("Chemical Nature, Sources & Health Effects")

    st.markdown(
        """
        Select a pollutant from the dropdown to see its **chemical identity**, **atmospheric reactions**, 
        and **health impacts**. This is the core *chemistry* part of the project.
        """
    )

    pollutant_keys = list(pollutant_info.keys())
    selected_pol = st.selectbox("Choose pollutant", pollutant_keys, format_func=lambda x: pollutant_info[x]["name"])

    info = pollutant_info[selected_pol]

    st.markdown('<div class="chem-card">', unsafe_allow_html=True)
    st.markdown(f"### {info['name']} ({info['formula']})")
    st.markdown(f"**Type:** {info['type']}")
    st.markdown(f"**Major sources:** {info['sources']}")
    st.markdown("**Atmospheric Chemistry / Reactions:**")
    st.code(info["chemistry"])

    st.markdown("**Health effects (chemistry link):**")
    st.markdown(info["health"])
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        """
        🔍 **Viva tip:**  
        - Explain how each pollutant is formed (combustion / oxidation / photochemistry),  
        - How it transforms in atmosphere (e.g. SO₂ → H₂SO₄, NO₂ → O₃),  
        - And how that connects to **AQI values** and **health impacts**.
        """
    )
