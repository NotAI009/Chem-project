# AQI Analysis using Python & Streamlit (Chemistry Project)

This project analyzes **Air Quality Index (AQI)** data using Python and Streamlit, with a strong focus on the **chemistry of air pollutants**.

## 🎯 Objective

- To study how pollutants like **PM₂.₅, PM₁₀, NO₂, SO₂, O₃, CO** affect the **Air Quality Index (AQI)**.
- To relate **atmospheric chemistry** (combustion, oxidation, photochemical reactions, acid rain, smog) with **real AQI data**.
- To visualize AQI trends for 4 Indian cities: **Bangalore, Delhi, Mumbai, Chennai** over **180 days**.

## 🧪 Chemistry Background

- **Combustion** of fossil fuels → CO, CO₂, NO, NO₂, SO₂, particulate matter.
- **Oxidation in atmosphere**:
  - SO₂ → SO₃ → H₂SO₄ (acid rain)
  - NO₂ + sunlight → NO + O· → O₃ (photochemical smog)
- **Particulate matter (PM₂.₅, PM₁₀)** contains sulfates, nitrates, organic compounds, metals.
- These species directly affect human health and are combined into a single number called **AQI**.

## 📂 Files in this Repository

- `app.py` – Main Streamlit application.
- `aqi_data_180_days.csv` – AQI dataset for Bangalore, Delhi, Mumbai, Chennai (180 days).
- `requirements.txt` – Python libraries required.
- `README.md` – Project documentation.

## 🚀 How to Run

1. Clone the repo or download the folder.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
