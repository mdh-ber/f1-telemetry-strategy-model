import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="PitSense AI",
    page_icon="🏎️",
    layout="wide"
)

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_data
def load_telemetry_data():
    return pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")


st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 30, 0, 0.25), transparent 35%),
        linear-gradient(135deg, #020202 0%, #090909 45%, #180000 100%);
    color: white;
}

.main-title {
    font-size: 60px;
    font-weight: 1000;
    color: #ff1e00;
    text-align: center;
    letter-spacing: 4px;
    text-shadow: 0 0 20px rgba(255,30,0,0.8);
}

.subtitle {
    text-align: center;
    color: #e5e7eb;
    font-size: 21px;
    margin-bottom: 30px;
}

.race-banner {
    background: linear-gradient(90deg, #ff1e00, #111, #ff1e00);
    padding: 12px;
    border-radius: 14px;
    text-align: center;
    font-weight: 800;
    letter-spacing: 2px;
    margin-bottom: 25px;
}

.card {
    background: rgba(255, 255, 255, 0.06);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255, 30, 0, 0.55);
    box-shadow: 0 0 30px rgba(255, 30, 0, 0.25);
}

.result-good {
    background: linear-gradient(135deg, #003b1f, #008f4c);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #00ff88;
    font-size: 25px;
    font-weight: 900;
    text-align: center;
}

.result-bad {
    background: linear-gradient(135deg, #4b0000, #c90000);
    padding: 24px;
    border-radius: 18px;
    border: 1px solid #ff3333;
    font-size: 25px;
    font-weight: 900;
    text-align: center;
}

.explanation-box {
    background: rgba(0, 0, 0, 0.55);
    padding: 22px;
    border-radius: 16px;
    border-left: 7px solid #ff1e00;
    font-size: 17px;
    line-height: 1.6;
}

[data-testid="stSidebar"] {
    background: #050505;
    border-right: 2px solid #ff1e00;
}

.stButton > button {
    background: linear-gradient(90deg, #ff1e00, #b00000);
    color: white;
    border: none;
    border-radius: 14px;
    font-weight: 900;
    height: 3.2rem;
}

.stButton > button:hover {
    box-shadow: 0 0 25px rgba(255, 30, 0, 0.9);
    color: white;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🏎️ PitSense AI</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Formula 1 Pit Stop Strategy Prediction & Telemetry Intelligence Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="race-banner">RACE CONTROL • STRATEGY WALL • PIT WINDOW SIMULATOR</div>',
    unsafe_allow_html=True
)

try:
    telemetry_df = load_telemetry_data()
except FileNotFoundError:
    st.warning("Telemetry dataset not found. Run the ML dataset creation script first.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏁 Pit Strategy Simulator",
    "📈 Telemetry Analytics",
    "⚔️ Driver Comparison",
    "🧾 Data Preview"
])

with tab1:
    st.sidebar.title("🏁 Race Control Panel")

    lap_number = st.sidebar.slider("Lap Number", 1, 100, 24)
    tyre_life = st.sidebar.slider("Tyre Life", 1, 80, 18)
    stint = st.sidebar.slider("Stint", 1, 10, 1)
    position = st.sidebar.slider("Track Position", 1, 20, 3)

    compound = st.sidebar.selectbox(
        "Tyre Compound",
        ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    )

    driver = st.sidebar.text_input("Driver Code", value="VER")

    col1, col2 = st.columns([1, 1.35])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏎️ Simulation Inputs")
        st.write(f"**Driver:** {driver}")
        st.write(f"**Current Lap:** {lap_number}")
        st.write(f"**Tyre Life:** {tyre_life} laps")
        st.write(f"**Current Stint:** {stint}")
        st.write(f"**Track Position:** P{position}")
        st.write(f"**Compound:** {compound}")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 Strategy Prediction Engine")

        if st.button("🚦 RUN PIT STRATEGY SIMULATION", use_container_width=True):
            payload = {
                "LapNumber": lap_number,
                "TyreLife": tyre_life,
                "Stint": stint,
                "Position": position,
                "Compound": compound,
                "Driver": driver
            }

            try:
                response = requests.post(
                    "http://backend:8000/predict-with-explanation",
                    json=payload,
                    timeout=10
                )

                if response.status_code == 200:
                    result = response.json()

                    pit_probability = result["probability_pit"] * 100
                    stay_probability = result["probability_no_pit"] * 100

                    if result["pit_stop_next_lap"] == 1:
                        decision = "PIT"
                        st.markdown(
                            '<div class="result-bad">⚠️ BOX NOW — PIT STOP LIKELY NEXT LAP</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        decision = "STAY OUT"
                        st.markdown(
                            '<div class="result-good">✅ STAY OUT — NO IMMEDIATE PIT STOP</div>',
                            unsafe_allow_html=True
                        )

                    m1, m2 = st.columns(2)

                    with m1:
                        st.metric("Pit Probability", f"{pit_probability:.1f}%")

                    with m2:
                        st.metric("Stay Out Probability", f"{stay_probability:.1f}%")

                    st.subheader("📊 Pit Strategy Confidence")
                    st.progress(int(pit_probability) / 100)

                    st.subheader("🤖 AI Strategy Explanation")
                    st.markdown(
                        f'<div class="explanation-box">{result["explanation"]}</div>',
                        unsafe_allow_html=True
                    )

                    st.session_state.history.append({
                        "Driver": driver,
                        "Lap": lap_number,
                        "TyreLife": tyre_life,
                        "Compound": compound,
                        "Position": position,
                        "Prediction": decision,
                        "PitProbability": round(pit_probability, 1)
                    })

                else:
                    st.error("Prediction API failed")

            except requests.exceptions.RequestException:
                st.error("Could not connect to backend API")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📜 Strategy Simulation History")

    if st.session_state.history:
        history_df = pd.DataFrame(st.session_state.history)
        st.dataframe(history_df, use_container_width=True)
    else:
        st.info("No simulations executed yet.")

with tab2:
    st.subheader("🎛️ Dynamic Telemetry Filters")

    filter_col1, filter_col2, filter_col3, filter_col4 = st.columns(4)

    available_drivers = sorted(telemetry_df["Driver"].unique())
    available_compounds = sorted(telemetry_df["Compound"].unique())
    available_stints = sorted(telemetry_df["Stint"].unique())

    with filter_col1:
        selected_drivers = st.multiselect(
            "Drivers",
            available_drivers,
            default=available_drivers[:3]
        )

    with filter_col2:
        selected_compounds = st.multiselect(
            "Tyre Compounds",
            available_compounds,
            default=available_compounds
        )

    with filter_col3:
        selected_stints = st.multiselect(
            "Stints",
            available_stints,
            default=available_stints
        )

    with filter_col4:
        min_lap = int(telemetry_df["LapNumber"].min())
        max_lap = int(telemetry_df["LapNumber"].max())

        selected_lap_range = st.slider(
            "Lap Range",
            min_lap,
            max_lap,
            (min_lap, max_lap)
        )

    filtered_df = telemetry_df[
        (telemetry_df["Driver"].isin(selected_drivers)) &
        (telemetry_df["Compound"].isin(selected_compounds)) &
        (telemetry_df["Stint"].isin(selected_stints)) &
        (telemetry_df["LapNumber"] >= selected_lap_range[0]) &
        (telemetry_df["LapNumber"] <= selected_lap_range[1])
    ]

    st.write(f"Filtered telemetry records: **{len(filtered_df)}**")

    analytics_col1, analytics_col2 = st.columns(2)

    with analytics_col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Filtered Lap Pace Analysis")

        if not filtered_df.empty:
            pace_chart_df = filtered_df.pivot_table(
                index="LapNumber",
                columns="Driver",
                values="LapTimeSeconds",
                aggfunc="mean"
            )
            st.line_chart(pace_chart_df)
        else:
            st.warning("No data available for selected filters.")

        st.markdown("</div>", unsafe_allow_html=True)

    with analytics_col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Filtered Tyre Compound Usage")

        if not filtered_df.empty:
            compound_counts = filtered_df["Compound"].value_counts()
            st.bar_chart(compound_counts)
        else:
            st.warning("No compound data available.")

        st.markdown("</div>", unsafe_allow_html=True)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric("Filtered Records", len(filtered_df))

    with metric_col2:
        st.metric("Drivers", filtered_df["Driver"].nunique() if not filtered_df.empty else 0)

    with metric_col3:
        st.metric("Compounds", filtered_df["Compound"].nunique() if not filtered_df.empty else 0)

    with metric_col4:
        avg_lap = filtered_df["LapTimeSeconds"].mean() if not filtered_df.empty else 0
        st.metric("Avg Lap Time", f"{avg_lap:.2f}s")

with tab3:
    st.subheader("⚔️ Driver Strategy Comparison")

    available_drivers = sorted(telemetry_df["Driver"].unique())

    compare_col1, compare_col2 = st.columns(2)

    driver_1 = compare_col1.selectbox(
        "Select Driver 1",
        available_drivers,
        index=0
    )

    driver_2 = compare_col2.selectbox(
        "Select Driver 2",
        available_drivers,
        index=1 if len(available_drivers) > 1 else 0
    )

    driver1_df = telemetry_df[telemetry_df["Driver"] == driver_1]
    driver2_df = telemetry_df[telemetry_df["Driver"] == driver_2]

    comparison_chart = pd.DataFrame({
        driver_1: driver1_df.groupby("LapNumber")["LapTimeSeconds"].mean(),
        driver_2: driver2_df.groupby("LapNumber")["LapTimeSeconds"].mean()
    })

    st.line_chart(comparison_chart)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        st.metric(
            f"{driver_1} Avg Lap",
            f"{driver1_df['LapTimeSeconds'].mean():.2f}s"
        )

    with metric_col2:
        st.metric(
            f"{driver_2} Avg Lap",
            f"{driver2_df['LapTimeSeconds'].mean():.2f}s"
        )

    with metric_col3:
        st.metric(
            f"{driver_1} Stints",
            int(driver1_df["Stint"].nunique())
        )

    with metric_col4:
        st.metric(
            f"{driver_2} Stints",
            int(driver2_df["Stint"].nunique())
        )

with tab4:
    st.subheader("🧾 Filtered Telemetry Data Preview")

    preview_drivers = st.multiselect(
        "Preview Drivers",
        sorted(telemetry_df["Driver"].unique()),
        default=sorted(telemetry_df["Driver"].unique())[:5]
    )

    preview_df = telemetry_df[telemetry_df["Driver"].isin(preview_drivers)]

    st.dataframe(
        preview_df[
            [
                "Driver",
                "LapNumber",
                "LapTimeSeconds",
                "Compound",
                "TyreLife",
                "Stint",
                "Position",
                "PitStopNextLap"
            ]
        ],
        use_container_width=True
    )