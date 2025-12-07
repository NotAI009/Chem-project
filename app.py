import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import requests

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AQI Analysis – Environmental Chemistry",
    layout="wide",
    page_icon="🌫️",
)

# -------------------------------------------------
# OPTIONAL: LOTTIE ANIMATION
# -------------------------------------------------
def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.json()
    except Exception:
        return None

try:
    from streamlit_lottie import st_lottie
    LOTTIE_AVAILABLE = True
except Exception:
    LOTTIE_AVAILABLE = False

lottie_pollution = load_lottie_url(
    "https://lottie.host/1eead027-0339-4c23-8974-7a73b094d737/z14L5RbbB8.json"
)

# -------------------------------------------------
# CUSTOM CSS (for bars / cards / dark UI)
# -------------------------------------------------
st.markdown(
    """
    <style>
    .main {
        background-color: #020617;
        color: #e5e7eb;
        font-family: "Segoe UI", system-ui, sans-serif;
    }
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 2.5rem;
        padding-left: 2.5rem;
        padding-right: 2.5rem;
    }
    h1, h2, h3, h4 {
        color: #e2e8f0;
        font-weight: 700;
    }
    .hero {
        padding: 1.5rem;
        border-radius: 1rem;
        background: radial-gradient(circle at top left, #22d3ee22, #0f172a 55%);
        border: 1px solid rgba(148, 163, 184, 0.5);
        box-shadow: 0 18px 45px rgba(15, 23, 42, 0.95);
    }
    .metric-card {
        padding: 1rem 1.2rem;
        border-radius: 0.9rem;
        background: rgba(15, 23, 42, 0.95);
        border: 1px solid rgba(148, 163, 184, 0.4);
        box-shadow: 0 10px 30px rgba(0,0,0,0.45);
    }
    .info-bar {
        padding: 0.9rem 1.1rem;
        border-radius: 0.7rem;
        background: linear-gradient(90deg, #0f172a, #020617);
        border-left: 4px solid #38bdf8;
        margin-bottom: 0.7rem;
    }
    .info-bar-chem {
        border-left-color: #22c55e;
    }
    .info-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #e5e7eb;
        margin-bottom: 0.2rem;
    }
    .info-body {
        font-size: 0.86rem;
        color: #cbd5f5;
    }
    .pill {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.8rem;
        border: 1px solid #38bdf8;
        color: #e0f2fe;
        background: #0f172a;
        margin-right: 0.4rem;
    }
    .aqi-chip-good {
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        border: 1px solid #16a34a;
        background: #16a34a22;
        color: #bbf7d0;
        margin-right: 0.25rem;
    }
    .aqi-chip-mod {
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        border: 1px solid #eab308;
        background: #eab30822;
        color: #fef3c7;
        margin-right: 0.25rem;
    }
    .aqi-chip-poor {
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        border: 1px solid #ef4444;
        background: #ef444422;
        color: #fecaca;
        margin-right: 0.25rem;
    }
    .badge-chem {
        background: #22c55e22;
        border: 1px solid #22c55e;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-right: 0.3rem;
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
        "type": "Primary & Secondary",
        "sources": "Vehicle exhaust, biomass burning, industrial emissions, secondary formation from SO₂ & NOₓ.",
        "chemistry": (
            "PM₂.₅ often contains sulfates (from SO₂ oxidation), nitrates (from NOₓ), "
            "organic carbon and metals. Because the particles are so small, they stay longer in air "
            "and penetrate deep into the lungs."
        ),
        "health": "Irritates lungs, reduces gas exchange, increases risk of asthma, bronchitis, and heart diseases."
    },
    "PM10": {
        "name": "Particulate Matter 10",
        "formula": "Mixture (≤ 10 μm)",
        "type": "Primary",
        "sources": "Dust, construction activities, road resuspension, burning of fuels.",
        "chemistry": (
            "Coarser particles containing dust, soil, metal oxides and carbonaceous material. "
            "They settle faster than PM₂.₅ but still affect the upper respiratory tract."
        ),
        "health": "Irritation of eyes, nose, throat; respiratory discomfort."
    },
    "NO2": {
        "name": "Nitrogen Dioxide",
        "formula": "NO₂",
        "type": "Primary & Secondary",
        "sources": "High-temperature combustion in vehicles, power plants and industries.",
        "chemistry": (
            "NO₂ is a key precursor of photochemical smog. Under sunlight:\n\n"
            "NO₂ + hν → NO + O·\n"
            "O· + O₂ → O₃\n\n"
            "This leads to ground-level ozone formation."
        ),
        "health": "Irritates respiratory tract, reduces lung function, aggravates asthma."
    },
    "SO2": {
        "name": "Sulfur Dioxide",
        "formula": "SO₂",
        "type": "Primary",
        "sources": "Burning of coal and oil containing sulfur, metal smelters.",
        "chemistry": (
            "SO₂ oxidises to SO₃ in air and then forms sulfuric acid:\n\n"
            "2 SO₂ + O₂ → 2 SO₃\n"
            "SO₃ + H₂O → H₂SO₄\n\n"
            "This is a major route for acid rain."
        ),
        "health": "Causes coughing, throat irritation, breathing difficulty; damages plant leaves."
    },
    "O3": {
        "name": "Ozone (tropospheric)",
        "formula": "O₃",
        "type": "Secondary",
        "sources": "Formed in atmosphere from NOₓ and VOCs in presence of sunlight.",
        "chemistry": (
            "O₃ is a strong oxidizing agent and a key component of photochemical smog. "
            "It is not emitted directly; it is formed by a series of reactions involving NO₂, O₂, "
            "and volatile organic compounds (VOCs)."
        ),
        "health": "Damages lung tissue, causes chest pain, coughing, and breathing problems."
    },
    "CO": {
        "name": "Carbon Monoxide",
        "formula": "CO",
        "type": "Primary",
        "sources": "Incomplete combustion of petrol, diesel, LPG, wood, etc.",
        "chemistry": (
            "CO binds strongly with hemoglobin to form carboxyhemoglobin (HbCO), "
            "reducing the oxygen-carrying capacity of blood."
        ),
        "health": "Headache, dizziness, unconsciousness; in high concentration it can be fatal."
    },
}

# -------------------------------------------------
# SIDEBAR – DATA LOADING
# -------------------------------------------------
st.sidebar.title("⚙️ Controls")

st.sidebar.write("Upload your own AQI CSV or use the project dataset:")

uploaded_file = st.sidebar.file_uploader(
    "Upload AQI CSV (optional)",
    type=["csv"],
    help="If you don't upload, the app tries to use 'aqi_data_180_days.csv' from the same folder.",
)

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
# HERO SECTION
# -------------------------------------------------
col_hero_text, col_hero_anim = st.columns([1.4, 1])

with col_hero_text:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown("### 1st Year Engineering – Chemistry Project")
    st.markdown("## 🌫️ AQI Analysis Dashboard – Environmental Chemistry Focus")

    st.markdown(
        """
        <span class="pill">Air Pollution Chemistry</span>
        <span class="pill">Atmospheric Reactions</span>
        <span class="pill">Health & Environment</span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        This dashboard connects **realistic AQI data** with **chemical concepts** such as:
        - combustion of fuels  
        - formation of photochemical smog  
        - acid rain and particle formation  
        - health effects of different pollutants  

        Built using **Python + Streamlit**, presented as a **Chemistry mini project**.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_hero_anim:
    if LOTTIE_AVAILABLE and lottie_pollution is not None:
        st_lottie(lottie_pollution, height=260)
    else:
        st.markdown(
            """
            <div class="metric-card">
            <b>Animation</b><br>
            Install <code>streamlit-lottie</code> to see a pollution animation here,
            or keep it like this for a simpler setup.
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("---")

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab_overview, tab_chem, tab_city, tab_health, tab_data = st.tabs(
    [
        "📊 Overview Dashboard",
        "🧪 Chemistry of Pollutants",
        "🏙️ City Air Profiles",
        "❤️ Health & AQI Categories",
        "📂 Data Explorer",
    ]
)

# -------------------------------------------------
# TAB 1: OVERVIEW
# -------------------------------------------------
with tab_overview:
    st.subheader("Overall AQI Snapshot")

    if df is None:
        st.warning("No data found. Upload a CSV or keep 'aqi_data_180_days.csv' with app.py.")
    else:
        required_cols = {"city", "AQI"}
        if not required_cols.issubset(df.columns):
            st.error("Dataset must contain at least 'city' and 'AQI' columns.")
        else:
            cities = sorted(df["city"].unique())

            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**Overall Average AQI**")
                st.markdown(f"<h2>{df['AQI'].mean():.1f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**Worst Recorded AQI**")
                st.markdown(f"<h2>{df['AQI'].max():.0f}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            with col3:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.markdown("**Number of Cities**")
                st.markdown(f"<h2>{len(cities)}</h2>", unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("")

            col_a, col_b = st.columns([1.4, 1])

            with col_a:
                fig_box = px.box(
                    df,
                    x="city",
                    y="AQI",
                    title="AQI range in each city",
                )
                fig_box.update_layout(template="plotly_dark", height=420)
                st.plotly_chart(fig_box, use_container_width=True)

            with col_b:
                st.markdown('<div class="info-bar info-bar-chem">', unsafe_allow_html=True)
                st.markdown('<div class="info-title">How to explain this in Chemistry viva?</div>', unsafe_allow_html=True)
                st.markdown(
                    """
                    <div class="info-body">
                    • A higher median AQI in a city suggests **more frequent build-up of pollutants**
                    like PM₂.₅, PM₁₀, NO₂, and SO₂.<br><br>
                    • This is usually due to **vehicle emissions, industrial combustion and biomass burning**.<br><br>
                    • A wider spread (tall box) indicates days with **very poor episodes**, often when
                    meteorological conditions trap pollutants near the surface (temperature inversion).
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.markdown('</div>', unsafe_allow_html=True)

            st.markdown("### AQI Distribution – All Cities Combined")
            fig_hist = px.histogram(
                df,
                x="AQI",
                nbins=30,
            )
            fig_hist.update_layout(template="plotly_dark", height=380)
            st.plotly_chart(fig_hist, use_container_width=True)

            st.markdown(
                """
                <div class="info-bar info-bar-chem">
                <div class="info-title">Chemistry view:</div>
                <div class="info-body">
                Every bar in this histogram represents how often certain <b>pollution levels</b> occur.  
                High AQI values mean <b>high concentration of chemically active pollutants</b> in the air – more 
                <b>oxidation, acid formation and smog</b> potential.
                </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------
# TAB 2: CHEMISTRY OF POLLUTANTS
# -------------------------------------------------
with tab_chem:
    st.subheader("Chemical Nature, Reactions & Health Effects")

    st.markdown(
        """
        <span class="badge-chem">Combustion of fuels</span>
        <span class="badge-chem">Acid rain</span>
        <span class="badge-chem">Photochemical smog</span>
        """,
        unsafe_allow_html=True,
    )

    pollutant_keys = list(pollutant_info.keys())
    selected_pol = st.selectbox(
        "Choose a pollutant to highlight",
        pollutant_keys,
        format_func=lambda x: pollutant_info[x]["name"],
    )
    info = pollutant_info[selected_pol]

    col_left, col_right = st.columns([1.1, 1])

    with col_left:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown(f"### {info['name']}  (`{info['formula']}`)")
        st.markdown(f"**Type:** {info['type']}")
        st.markdown(f"**Typical sources:** {info['sources']}")
        st.markdown("**Health effects (chemistry link):**")
        st.markdown(info["health"])
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.markdown("**Important atmospheric reactions:**")
        st.code(info["chemistry"])
        st.markdown(
            """
            AQI for this pollutant increases when its **ambient concentration** goes up.  
            Because it participates in **oxidation and acid-forming reactions**, even moderate
            levels can have serious environmental effects.
            """
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    if df is not None and selected_pol in df.columns:
        st.markdown(f"### Dataset view: {info['name']} levels across all cities")
        fig_pol = px.box(
            df,
            x="city",
            y=selected_pol,
            title=f"{selected_pol} concentration by city",
        )
        fig_pol.update_layout(template="plotly_dark", height=430)
        st.plotly_chart(fig_pol, use_container_width=True)

        st.markdown(
            f"""
            <div class="info-bar info-bar-chem">
            <div class="info-title">How to talk about this:</div>
            <div class="info-body">
            You can compare which city shows higher <b>{info['name']}</b> in the box plot and relate it to
            local <b>sources</b> (traffic, industry, coastal breeze, etc.).<br><br>
            Then you can connect it to the <b>chemical reactions</b> shown above and explain why
            this pollutant is dangerous even if its concentration seems small.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------
# TAB 3: CITY AIR PROFILES
# -------------------------------------------------
with tab_city:
    st.subheader("City-wise AQI & Pollutant Profile")

    if df is None:
        st.warning("No data found.")
    else:
        if not {"city", "date", "AQI"}.issubset(df.columns):
            st.error("Dataset must contain 'city', 'date' and 'AQI' columns.")
        else:
            cities = sorted(df["city"].unique())
            city_sel = st.selectbox("Select city", cities)

            df_city = df[df["city"] == city_sel].copy().sort_values("date")

            col_top_l, col_top_r = st.columns([1.4, 1])

            with col_top_l:
                st.markdown(f"### AQI over time – {city_sel}")
                fig_ts = px.line(
                    df_city,
                    x="date",
                    y="AQI",
                    markers=True,
                )
                fig_ts.update_layout(template="plotly_dark", height=420)
                st.plotly_chart(fig_ts, use_container_width=True)

            with col_top_r:
                st.markdown(
                    """
                    <div class="info-bar info-bar-chem">
                    <div class="info-title">How to explain this graph:</div>
                    <div class="info-body">
                    • Peaks in AQI correspond to days with <b>high pollutant load</b> – for example,
                    heavy traffic, industrial activity, or stagnant weather.<br><br>
                    • Chemically, more pollutants mean more reactions: oxidation of SO₂ to H₂SO₄,
                    NO₂ to O₃, and formation of secondary particles.<br><br>
                    • You can pick one peak, mention its approximate value, and say: “On such days,
                    the atmosphere above this city behaves like a small chemical reactor full of
                    oxidizing species.”
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            pol_cols = [p for p in ["PM2_5", "PM10", "NO2", "SO2", "O3", "CO"] if p in df_city.columns]

            if pol_cols:
                st.markdown(f"### Average pollutant composition – {city_sel}")
                mean_vals = df_city[pol_cols].mean().reset_index()
                mean_vals.columns = ["Pollutant", "Mean_concentration"]

                fig_bar = px.bar(
                    mean_vals,
                    x="Pollutant",
                    y="Mean_concentration",
                )
                fig_bar.update_layout(template="plotly_dark", height=380)
                st.plotly_chart(fig_bar, use_container_width=True)

                st.markdown(
                    """
                    <div class="info-bar info-bar-chem">
                    <div class="info-title">Chemical interpretation:</div>
                    <div class="info-body">
                    • Higher bars for PM₂.₅ / PM₁₀ → <b>particulate pollution</b> is dominant.  
                    • Higher NO₂ / SO₂ → strong influence of <b>combustion sources</b> like vehicles and power plants.  
                    • O₃ presence indicates <b>photochemical reactions</b> driven by sunlight.  
                    Use this to compare cities and say which pollutants dominate each one.
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# -------------------------------------------------
# TAB 4: HEALTH & AQI CATEGORIES
# -------------------------------------------------
with tab_health:
    st.subheader("AQI Categories, Health Effects & Days Count")

    st.markdown(
        """
        <div class="info-bar info-bar-chem">
        <div class="info-title">AQI interpretation (generic scale)</div>
        <div class="info-body">
        <span class="aqi-chip-good">0–50: Good</span>
        <span class="aqi-chip-mod">51–100: Moderate</span>
        <span class="aqi-chip-poor">101–200: Unhealthy for sensitive groups</span><br>
        201–300: Very Unhealthy • Above 300: Hazardous
        </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if df is None or "AQI" not in df.columns or "city" not in df.columns:
        st.warning("Dataset with 'AQI' and 'city' is required.")
    else:
        def classify_aqi(aqi):
            if aqi <= 50:
                return "Good"
            elif aqi <= 100:
                return "Moderate"
            elif aqi <= 200:
                return "Unhealthy (Sensitive)"
            elif aqi <= 300:
                return "Very Unhealthy"
            else:
                return "Hazardous"

        df_cat = df.copy()
        df_cat["AQI_Category"] = df_cat["AQI"].apply(classify_aqi)

        cities = sorted(df_cat["city"].unique())
        city_sel = st.selectbox("Select city to see AQI category days", cities)

        df_city = df_cat[df_cat["city"] == city_sel]
        cat_counts = df_city["AQI_Category"].value_counts().reset_index()
        cat_counts.columns = ["AQI_Category", "Days"]

        fig_cat = px.bar(
            cat_counts,
            x="AQI_Category",
            y="Days",
        )
        fig_cat.update_layout(template="plotly_dark", height=380)
        st.plotly_chart(fig_cat, use_container_width=True)

        st.markdown(
            f"""
            <div class="info-bar info-bar-chem">
            <div class="info-title">How to talk about this in viva:</div>
            <div class="info-body">
            For <b>{city_sel}</b>, you can say: “Out of the total days in the dataset, most days fall
            in the <b>{cat_counts.iloc[0]['AQI_Category']}</b> category.”<br><br>
            Then you connect it with chemistry:<br>
            • Frequent <b>Unhealthy</b> days mean prolonged exposure to oxidizing gases (O₃, NO₂), acidic species (H₂SO₄, HNO₃ aerosols) and fine particles.<br>
            • This leads to irritation of respiratory tract, corrosion of materials, and damage to plants.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -------------------------------------------------
# TAB 5: DATA EXPLORER
# -------------------------------------------------
with tab_data:
    st.subheader("Raw Data Explorer")

    if df is None:
        st.warning("No data available.")
    else:
        st.markdown(
            """
            <div class="info-bar">
            <div class="info-title">How this supports your project:</div>
            <div class="info-body">
            You can mention that you used <b>Python (Pandas)</b> to handle and filter the AQI dataset,  
            which is a realistic way scientists and environmental engineers analyse air quality data.
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "city" in df.columns:
            cities = sorted(df["city"].unique())
            city_filter = st.multiselect("Filter by city", cities, default=cities)
            df_filtered = df[df["city"].isin(city_filter)].copy()
        else:
            df_filtered = df.copy()

        if "date" in df_filtered.columns and df_filtered["date"].notna().any():
            df_filtered = df_filtered.sort_values("date")
            min_date = df_filtered["date"].min()
            max_date = df_filtered["date"].max()
            start_date, end_date = st.slider(
                "Filter by date range",
                min_value=min_date.to_pydatetime(),
                max_value=max_date.to_pydatetime(),
                value=(min_date.to_pydatetime(), max_date.to_pydatetime()),
            )
            mask = (df_filtered["date"] >= pd.to_datetime(start_date)) & (
                df_filtered["date"] <= pd.to_datetime(end_date)
            )
            df_filtered = df_filtered[mask]

        st.dataframe(df_filtered, use_container_width=True, height=450)
