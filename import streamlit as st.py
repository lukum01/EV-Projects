import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

# -----------------------------
# Configuration Section
# -----------------------------
CONFIG = {
    "battery_options": {
        "61 kWh": 58.6,
        "49 kWh": 47.46
    },
    "temperature_rates": {
        "61": {
            "0-15": {"city": 0.16129, "highway": 0.1677, "expressway": 0.1934, "hilly": 0.32154},
            "15-25": {"city": 0.13175, "highway": 0.14641, "expressway": 0.16597, "hilly": 0.27548},
            "25-35": {"city": 0.12254, "highway": 0.13755, "expressway": 0.1536, "hilly": 0.2551},
            "35-45": {"city": 0.13679, "highway": 0.1466, "expressway": 0.1659, "hilly": 0.27528}
        },
        "49": {
            "0-15": {"city": 0.1425, "highway": 0.1638, "expressway": 0.2005, "hilly": 0.2709},
            "15-25": {"city": 0.1281, "highway": 0.1425, "expressway": 0.1720, "hilly": 0.2264},
            "25-35": {"city": 0.1179, "highway": 0.1328, "expressway": 0.1576, "hilly": 0.2456},
            "35-45": {"city": 0.1330, "highway": 0.1442, "expressway": 0.1720, "hilly": 0.2678}
        }
    },

}

# -----------------------------
# Utility Functions
# -----------------------------
def normalize_battery_key(capacity):
    return "49" if capacity < 55 else "61"

def get_rate_set(temp, battery_capacity):
    battery_key = normalize_battery_key(battery_capacity)
    if temp <= 15:
        return CONFIG["temperature_rates"][battery_key]["0-15"]
    elif temp <= 25:
        return CONFIG["temperature_rates"][battery_key]["15-25"]
    elif temp <= 35:
        return CONFIG["temperature_rates"][battery_key]["25-35"]
    else:
        return CONFIG["temperature_rates"][battery_key]["35-45"]

def estimate_range(battery_capacity_kwh, city_rate, highway_rate, expressway_rate, hilly_rate, city_pct, highway_pct, expressway_pct, hilly_pct):
    effective_consumption = (
        city_pct * city_rate +
        highway_pct * highway_rate +
        expressway_pct * expressway_rate +
        hilly_pct * hilly_rate
    )
    return round(battery_capacity_kwh / effective_consumption)

# -----------------------------
# Streamlit UI Section
# -----------------------------
st.set_page_config(page_title="EV Range Dashboard", layout="wide")
st.title("🔋 EV Range Calculator Dashboard")
st.markdown("Estimate the driving range of your EV based on temperature and driving conditions.")

# -----------------------------
# Input Section
# -----------------------------
st.header("Vehicle battery pack")
battery_pack_choice = st.selectbox("Choose your battery pack:", list(CONFIG["battery_options"].keys()), index=0)
battery_capacity = CONFIG["battery_options"][battery_pack_choice]

temp = st.slider("Select Outside temperature (°C):", min_value=0, max_value=45, value=20, step=5)
rates = get_rate_set(temp, battery_capacity)

if temp <= 15:
    st.info("⚠️ Cold temperatures may reduce efficiency.")
elif temp >= 35:
    st.warning("⚠️ High temperatures may increase consumption.")
else:
    st.success("✅ Optimal temperature range for EV efficiency.")

st.subheader("Driving Mix (%)")
with st.expander("ℹ️ What do these driving types mean?"):
    st.markdown("""
    - **City**: Frequent stops, low speed, high regeneration.
    - **Highway**: Moderate speed, steady driving.
    - **Expressway**: High speed, minimal stops.
    - **Hilly**: Inclines/declines, higher load on battery.
    """)

col1, col2, col3, col4 = st.columns(4)
city = col1.number_input("City", min_value=0, max_value=100, value=30)
highway = col2.number_input("Highway", min_value=0, max_value=100, value=30)
expressway = col3.number_input("Expressway", min_value=0, max_value=100, value=30)
hilly = col4.number_input("Hilly- Up hill", min_value=0, max_value=100, value=10)

# -----------------------------
# Calculation Section
# -----------------------------
total_mix = city + highway + expressway + hilly
if total_mix != 100:
    st.error("Driving mix percentages must add up to 100%.")
else:
    city_pct = city / 100
    highway_pct = highway / 100
    expressway_pct = expressway / 100
    hilly_pct = hilly / 100

    raw_range_km = estimate_range(
        battery_capacity,
        rates["city"],
        rates["highway"],
        rates["expressway"],
        rates["hilly"],
        city_pct,
        highway_pct,
        expressway_pct,
        hilly_pct
    )

    final_range_km = raw_range_km

    # -----------------------------
    # Results and Charts Section
    # -----------------------------
    st.header("Results")
    st.success(f"✅ Estimated EV Range: **{final_range_km} km**")

# -----------------------------
# Footer Section
# -----------------------------
st.markdown("<div style='text-align: right; font-size: 12px; color: black;'>Prepared by ムクル</div>", unsafe_allow_html=True)
