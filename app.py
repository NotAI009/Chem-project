import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import json
import requests

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="AQI Analysis – Chemistry & Math",
    layout="wide",
    page_icon="🌫️",
)

# -------------------------------------------------
# LOTTIE HELPER (for animation)
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

# A nice pollution-themed animation (if internet is available)
lottie_pollution = load_lottie_url(
    "https://lottie.host/1eead027-0339-4c23-8974-7a73b094d737/z14L5RbbB8.json"
)

# -------------------------------------------------
# CUSTOM CSS
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
    .badge-chem {
        background: #22c55e22;
        border: 1px solid #22c55e;
        padding: 0.15rem 0.55rem;
        border-radius: 999px;
        font-size: 0.78rem;
        margin-right: 0.3rem;
    }
    .badge-math {
        background: #38bdf822;
        border: 1px solid #38bdf8;
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
        "type": "Primary & Secondary Pollutant",
        "sources": "Vehicle exhaust, biomass burning, industrial emissions, secondary formation from SO₂ & NOₓ.",
        "chemistry": (
            "PM₂.₅ often contains sulfates (from SO₂ oxidation), nitrates (from NOₓ), "
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
            "Less deep penetration than PM₂.₅ but still harmful."
        ),
        "health": "Irritation of eyes, nose, throat; respiratory problems."
    },
    "NO2": {
        "name": "Nitrogen Dioxide",
        "formula": "NO₂",
        "type": "Primary & Secondary Pollutant",
        "sources": "High-temperature combustion in vehicles, power plants, industries.",
        "chemistry": (
            "Participates in photochemical smog. Under sunlight it forms NO and atomic oxygen:\n\n"
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
            "Oxidizes in atmosphere to SO₃, then forms sulfuric acid:\n\n"
            "2 SO₂ + O₂ → 2 SO₃\nSO₃ + H₂O → H₂SO₄\n\n"
            "Major contributor to acid rain."
        ),
        "health": "Causes irritation in eyes, nose, throat; breathing difficulty; plant damage."
    },
    "O3": {
        "name": "Ozone (tropospheric)",
        "formula": "O₃",
        "type": "Secondary Pollutant",
        "sources": "Formed from NOₓ and VOCs under sunlight.",
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
            "Binds strongly with hemoglobin to form carboxyhemoglobin (HbCO), reducing oxygen transport in blood."
        ),
        "health": "Reduces oxygen supply, causes headache, dizziness; high levels can be fatal."
    },
}

# -------------------------------------------------
# SIDEBAR – DATA LOADING
# -------------------------------------------------
st.sidebar.title("⚙️ Controls")

st.sidebar.write("Upload your own AQI CSV or use the default project dataset.")

uploaded_file = st.sidebar.file_uploader(
    "Upload AQI CSV file (optional)",
    type=["csv"],
    help="If you don't upload, the app will try to use 'aqi_data_180_days.csv' from the project folder.",
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
    st.markdown("## 🌫️ AQI Analysis Dashboard – **Chemistry + Math + Python**")

    st.markdown(
        """
        <span class="pill">Environmental Chemistry</span>
        <span class="pill">Atmospheric Reactions</span>
        <span class="pill">Integration & Matrices</span>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        This interactive dashboard connects:

        - **Chemistry:** Combustion, oxidation, acid rain, photochemical smog  
        - **Maths:** Integration, differentiation, matrices, eigenvalues  
        - **Programming:** Python, Pandas, NumPy, Plotly, Streamlit  

        using real-like **AQI data** for Indian cities.
        """
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col_hero_anim:
    if LOTTIE_AVAILABLE and lottie_pollution is not None:
        st_lottie(lottie_pollution, height=260)
    else:
        st.markdown("*(Animation placeholder – install `streamlit-lottie` for Lottie support.)*")

st.markdown("---")

# -------------------------------------------------
# TABS
# -------------------------------------------------
tab_dash, tab_chem, tab_trends, tab_math, tab_data = st.tabs(
    [
        "📊 Dashboard",
        "🧪 Chemistry of Pollutants",
        "📈 Time Trends",
        "📐 Math & Modeling",
        "📂 Data Explorer",
    ]
)

# -------------------------------------------------
# TAB: DASHBOARD
# -------------------------------------------------
with tab_dash:
    st.subheader("Overall Air Quality Snapshot")

    if df is None:
        st.warning("No data found. Upload a CSV or keep 'aqi_data_180_days.csv' in the project folder.")
    else:
        if "city" not in df.columns or "AQI" not in df.columns:
            st.error("Dataset must contain at least 'city', 'date' and 'AQI' columns.")
        else:
            # Summary per city
            city_group = df.groupby("city")["AQI"]

            col1, col2, col3, col4 = st.columns(4)
            city_names = sorted(df["city"].unique())

            metric_cols = [col1, col2, col3, col4]
            for col, city in zip(metric_cols, city_names):
                with col:
                    city_df = df[df["city"] == city]
                    avg_aqi = city_df["AQI"].mean()
                    max_aqi = city_df["AQI"].max()
                    min_aqi = city_df["AQI"].min()
                    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                    st.markdown(f"**{city}**")
                    st.metric("Avg AQI", f"{avg_aqi:.1f}")
                    st.caption(f"Max: {max_aqi:.0f}  •  Min: {min_aqi:.0f}")
                    st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("### AQI Category Bar (Chemistry Interpretation)")

            fig_box = px.box(
                df,
                x="city",
                y="AQI",
                title="AQI range per city",
            )
            fig_box.update_layout(template="plotly_dark", height=420)
            st.plotly_chart(fig_box, use_container_width=True)

            st.markdown(
                """
                **Chemistry view:**  
                - Higher **median AQI** indicates more intense and frequent pollutant build-up – usually from **vehicle exhaust, industries, and biomass burning**.  
                - Wider spread (big box & whiskers) means AQI is **highly variable**, often due to changing **meteorological conditions** (wind, inversion) and **emission peaks**.
                """
            )

# -------------------------------------------------
# TAB: CHEMISTRY
# -------------------------------------------------
with tab_chem:
    st.subheader("Chemical Nature, Reactions & Health Effects")

    st.markdown(
        """
        This section highlights the **chemical identity** of each pollutant,  
        along with **reactions in the atmosphere** and **health impacts**.
        """
    )

    st.markdown(
        """
        <span class="badge-chem">Acid rain</span>
        <span class="badge-chem">Photochemical smog</span>
        <span class="badge-chem">Oxidation reactions</span>
        """,
        unsafe_allow_html=True,
    )

    pollutant_keys = list(pollutant_info.keys())
    selected_pol = st.selectbox(
        "Choose pollutant",
        pollutant_keys,
        format_func=lambda x: pollutant_info[x]["name"],
    )

    info = pollutant_info[selected_pol]

    st.markdown("-----")
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.markdown("### Identity & Sources")
        st.markdown(f"**Name:** {info['name']}")
        st.markdown(f"**Formula:** `{info['formula']}`")
        st.markdown(f"**Type:** {info['type']}")
        st.markdown(f"**Major Sources:** {info['sources']}")

        st.markdown("### Health Effects")
        st.markdown(info["health"])

    with col_right:
        st.markdown("### Atmospheric Chemistry")
        st.code(info["chemistry"])

        st.markdown("### Chemistry Link to AQI")
        st.markdown(
            """
            - Higher concentration of this pollutant increases the **AQI sub-index** for that pollutant.  
            - The final AQI is usually determined by the **worst (highest) sub-index**, so a spike in one pollutant can
              dominate the overall AQI.
            """
        )

    st.markdown("---")
    st.markdown("#### Example: Photochemical Smog Formation (NO₂ & O₃)")

    st.latex(r"\text{NO}_2 + h\nu \rightarrow \text{NO} + O\cdot")
    st.latex(r"O\cdot + O_2 \rightarrow O_3")
    st.latex(r"O_3 + \text{VOCs} \rightarrow \text{Oxidants (smog components)}")

    st.markdown(
        """
        In your viva you can connect **NO₂ levels** in the data to **O₃ formation** and **smog episodes** 
        using these equations.
        """
    )

# -------------------------------------------------
# TAB: TIME TRENDS
# -------------------------------------------------
with tab_trends:
    st.subheader("Time Series of AQI & Pollutants")

    if df is None:
        st.warning("No data found.")
    else:
        if "city" not in df.columns or "date" not in df.columns:
            st.error("Dataset must contain 'city' and 'date' columns.")
        else:
            cities = sorted(df["city"].unique())
            col_sel1, col_sel2 = st.columns([1, 1])

            with col_sel1:
                city_selected = st.selectbox("Select City", cities)

            with col_sel2:
                var_options = ["AQI", "PM2_5", "PM10", "NO2", "SO2", "O3", "CO"]
                var_options = [v for v in var_options if v in df.columns]
                var_selected = st.selectbox("Select variable", var_options)

            city_df = df[df["city"] == city_selected].copy()
            city_df = city_df.sort_values("date")

            st.markdown(f"### {var_selected} over time – {city_selected}")

            fig_ts_var = px.line(
                city_df,
                x="date",
                y=var_selected,
                markers=True,
            )
            fig_ts_var.update_layout(template="plotly_dark", height=430)
            st.plotly_chart(fig_ts_var, use_container_width=True)

            st.markdown(
                f"""
                - Peaks in **{var_selected}** often correspond to **episodes of poor air quality**,  
                  such as high traffic, festivals with firecrackers, crop burning, or stagnant air.  
                - From a chemistry point of view, these peaks mean higher concentrations of reactive gases/particles 
                  involved in **oxidation, acid formation and smog**.
                """
            )

# -------------------------------------------------
# TAB: MATH & MODELING
# -------------------------------------------------
with tab_math:
    st.subheader("Math & Modeling – Integration, Differentiation, Matrices")

    st.markdown(
        """
        This tab shows how **mathematics** is used to analyse AQI data:

        <span class="badge-math">Integration (cumulative exposure)</span>
        <span class="badge-math">Differentiation (rate of change)</span>
        <span class="badge-math">Matrices & Eigenvalues</span>
        """,
        unsafe_allow_html=True,
    )

    if df is None:
        st.warning("No data found.")
    else:
        if "city" not in df.columns or "date" not in df.columns or "AQI" not in df.columns:
            st.error("Dataset needs 'city', 'date', 'AQI' and pollutant columns.")
        else:
            cities = sorted(df["city"].unique())
            city_math = st.selectbox("Select city for mathematical analysis", cities)

            df_city = df[df["city"] == city_math].copy().sort_values("date")
            df_city = df_city.reset_index(drop=True)

            # ---- Integration: cumulative AQI exposure ----
            st.markdown("### 1. Integration – Cumulative AQI Exposure")

            st.latex(r"\text{Exposure} \approx \int_{t_0}^{t_n} AQI(t)\, dt")

            # Use trapezoidal rule; assume 1 day step
            if len(df_city) > 1:
                exposure = np.trapz(df_city["AQI"].values, dx=1)
            else:
                exposure = 0.0

            st.markdown(
                f"""
                Approximate **cumulative AQI exposure** for **{city_math}** over the recorded period:

                - Number of days: `{len(df_city)}`  
                - Integral of AQI(t) dt ≈ **{exposure:.1f} (AQI·day)**  

                This represents the **total pollution load** a person is exposed to over time,  
                similar to the area under the AQI–time graph.
                """
            )

            fig_exposure = px.area(
                df_city,
                x="date",
                y="AQI",
                title=f"AQI vs Time – Area under curve ≈ cumulative exposure ({city_math})",
            )
            fig_exposure.update_layout(template="plotly_dark", height=430)
            st.plotly_chart(fig_exposure, use_container_width=True)

            st.markdown("---")

            # ---- Differentiation: rate of change of AQI ----
            st.markdown("### 2. Differentiation – Rate of Change of AQI")

            st.latex(r"\frac{d(AQI)}{dt} \approx AQI_{i} - AQI_{i-1}")

            df_city["dAQI_dt"] = df_city["AQI"].diff()

            fig_diff = px.bar(
                df_city,
                x="date",
                y="dAQI_dt",
                title=f"Approximate daily change in AQI – {city_math}",
            )
            fig_diff.update_layout(template="plotly_dark", height=430)
            st.plotly_chart(fig_diff, use_container_width=True)

            st.markdown(
                """
                - Positive bars → AQI **increasing** (air getting worse).  
                - Negative bars → AQI **decreasing** (air improving).  

                In viva, you can say you used **numerical differentiation** to estimate how fast air quality
                is changing from day to day.
                """
            )

            st.markdown("---")

            # ---- Matrix & Eigenvalues: pollutant covariance ----
            st.markdown("### 3. Matrices & Eigenvalues – Pollution Patterns")

            st.markdown(
                """
                We form a **data matrix** using pollutant concentrations and study its **covariance matrix**.

                If we denote the pollutant vector as:

                \\[
                \\vec{x} = 
                \\begin{bmatrix}
                \\text{PM}_{2.5} \\\\
                \\text{PM}_{10} \\\\
                \\text{NO}_2 \\\\
                \\text{SO}_2 \\\\
                O_3 \\\\
                CO
                \\end{bmatrix}
                \\]

                then the covariance matrix **C** is:

                \\[
                C = \\text{cov}(\\vec{x}) 
                \\]

                We then compute **eigenvalues and eigenvectors** of C.
                """
            )

            pol_cols = [c for c in ["PM2_5", "PM10", "NO2", "SO2", "O3", "CO"] if c in df_city.columns]

            if len(pol_cols) >= 2:
                X = df_city[pol_cols].values
                # subtract mean
                X_centered = X - X.mean(axis=0)
                cov = np.cov(X_centered, rowvar=False)

                eig_vals, eig_vecs = np.linalg.eig(cov)

                cov_df = pd.DataFrame(cov, index=pol_cols, columns=pol_cols)
                eig_df = pd.DataFrame(
                    {
                        "Eigenvalue": eig_vals,
                        "Explained_variance_%": eig_vals / eig_vals.sum() * 100,
                    }
                )

                st.markdown("#### Covariance Matrix of Pollutants")
                st.dataframe(cov_df.style.format("{:.2f}"), use_container_width=True)

                st.markdown("#### Eigenvalues (Pollution Modes)")
                st.dataframe(eig_df.style.format({"Eigenvalue": "{:.2f}", "Explained_variance_%": "{:.2f}"}))

                st.markdown(
                    """
                    **How to explain this in viva:**

                    - We treat pollutants as components of a **vector** and study how they **vary together**.  
                    - The covariance matrix tells us which pollutants **co-vary strongly** (e.g., PM₂.₅ & PM₁₀).  
                    - Eigenvalues show the strength of independent **pollution patterns**.  
                    - The largest eigenvalue corresponds to a dominant combination of pollutants (e.g. traffic-related mix).
                    """
                )
            else:
                st.info("Not enough pollutant columns to form a covariance matrix (need at least 2).")

# -------------------------------------------------
# TAB: DATA EXPLORER
# -------------------------------------------------
with tab_data:
    st.subheader("Raw Data Explorer")

    if df is None:
        st.warning("No data available.")
    else:
        st.markdown("Use filters to inspect specific cities and date ranges.")

        cities = sorted(df["city"].unique()) if "city" in df.columns else []
        if cities:
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

        st.markdown(
            """
            In your report, you can mention that you used **Python (Pandas)** to handle and filter the dataset  
            before performing chemical and mathematical analysis.
            """
        )
