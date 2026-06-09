import streamlit as st
import requests
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="PitSense AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_API = "http://backend:8000"
HERO_IMAGE = Path("frontend/assets/f1_car.png")

RACE_DATA_FILES = [
    Path("data/monaco_2024_race.csv"),
    Path("../data/monaco_2024_race.csv"),
    Path("data/multi_race_2024_raw.csv"),
    Path("../data/multi_race_2024_raw.csv"),
]

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_data(ttl=60)
def get_summary():
    return requests.get(f"{BASE_API}/analytics/summary", timeout=10).json()


@st.cache_data(ttl=60)
def get_drivers():
    return requests.get(f"{BASE_API}/analytics/drivers", timeout=10).json()["drivers"]


def get_driver_data(driver):
    return requests.get(f"{BASE_API}/analytics/driver/{driver}", timeout=10).json()


@st.cache_data
def load_race_dataframe():
    for file_path in RACE_DATA_FILES:
        if file_path.exists():
            df = pd.read_csv(file_path)

            if "LapTime" in df.columns:
                df["LapTimeSeconds"] = pd.to_timedelta(
                    df["LapTime"],
                    errors="coerce"
                ).dt.total_seconds()

                # Remove invalid / unrealistic laps
                df = df[
                    (df["LapTimeSeconds"].notna()) &
                    (df["LapTimeSeconds"] > 60) &
                    (df["LapTimeSeconds"] < 200)
                ]

            return df

    return None


try:
    summary = get_summary()
    drivers = get_drivers()
except Exception:
    st.error("Backend API is not available. Start Docker Compose and FastAPI first.")
    st.stop()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #05070d 0%, #070b12 45%, #020202 100%);
    color: white;
}

.block-container {
    padding-top: 1rem;
    max-width: 1450px;
}

.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 20px 0 24px 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.f1-logo {
    color: #ff1e00;
    font-size: 36px;
    font-weight: 1000;
    letter-spacing: -3px;
    padding-right: 20px;
    border-right: 1px solid rgba(255,255,255,0.28);
}

.brand-text {
    font-size: 26px;
    font-weight: 900;
}

.brand-text span {
    color: #ff1e00;
}

.nav-note {
    font-size: 13px;
    font-weight: 800;
    color: #cbd5e1;
}

.hero-title {
    font-size: 64px;
    line-height: 1;
    font-weight: 1000;
}

.hero-title span {
    color: #ff1e00;
}

.hero-copy {
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.7;
    margin-top: 22px;
    max-width: 560px;
}

.hero-image-box {
    background: radial-gradient(circle at center, rgba(255,30,0,0.25), transparent 55%);
    border-radius: 26px;
    border: 1px solid rgba(255,255,255,0.10);
    padding: 10px;
    box-shadow: 0 0 70px rgba(255,30,0,0.20);
}

.metric-card, .panel, .feature-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 18px;
    padding: 26px;
}

.metric-value {
    color: white;
    font-size: 38px;
    font-weight: 900;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
}

.section-title {
    font-size: 36px;
    font-weight: 900;
    margin: 45px 0 20px 0;
}

.result-red {
    background: rgba(255,30,0,0.14);
    border: 1px solid rgba(255,30,0,0.55);
    color: #ff3b30;
    padding: 22px;
    border-radius: 14px;
    font-weight: 900;
    font-size: 18px;
}

.result-green {
    background: rgba(0,180,100,0.14);
    border: 1px solid rgba(0,255,136,0.45);
    color: #00ff88;
    padding: 22px;
    border-radius: 14px;
    font-weight: 900;
    font-size: 18px;
}

.ai-box {
    border-left: 5px solid #ff1e00;
    background: rgba(0,0,0,0.45);
    padding: 20px;
    border-radius: 12px;
    line-height: 1.7;
    color: #dbeafe;
}

.stButton > button {
    background: linear-gradient(90deg, #ff1e00, #d40000);
    color: white;
    border: none;
    border-radius: 10px;
    height: 3.2rem;
    font-weight: 900;
}

.stButton > button:hover {
    box-shadow: 0 0 28px rgba(255,30,0,0.55);
    color: white;
}

[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)


st.markdown("""
<div class="topbar">
    <div class="brand">
        <div class="f1-logo">F1</div>
        <div class="brand-text">PITSENSE <span>AI</span></div>
    </div>
    <div class="nav-note">AI Strategy Platform • Telemetry Intelligence • F1 Analytics</div>
</div>
""", unsafe_allow_html=True)


tab_home, tab_features, tab_sim, tab_analytics, tab_about, tab_docs = st.tabs(
    ["HOME", "FEATURES", "SIMULATOR", "ANALYTICS", "ABOUT", "DOCUMENTATION"]
)


with tab_home:
    left, right = st.columns([1, 1.15])

    with left:
        st.markdown("""
        <div class="kicker">AI-POWERED F1 STRATEGY PLATFORM</div>
        <div class="hero-title">
            INTELLIGENT STRATEGY.<br>
            <span>FASTER DECISIONS.</span><br>
            RACE AHEAD.
        </div>
        <div class="hero-copy">
            PitSense AI analyzes race telemetry, tyre conditions, stint behavior,
            and machine learning predictions to support faster pit stop strategy
            decisions with AI-generated race engineer explanations.
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="hero-image-box">', unsafe_allow_html=True)
        if HERO_IMAGE.exists():
            st.image(str(HERO_IMAGE), use_container_width=True)
        else:
            st.warning("Add your F1 car image at frontend/assets/f1_car.png")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Platform Metrics</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    metrics = [
        ("Telemetry Records", summary["total_records"]),
        ("Drivers", summary["total_drivers"]),
        ("Tyre Compounds", summary["total_compounds"]),
        ("Average Lap Time", f"{summary['average_lap_time']:.2f}s"),
    ]

    for col, item in zip([c1, c2, c3, c4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{item[1]}</div>
                    <div class="metric-label">{item[0]}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


with tab_features:
    st.markdown('<div class="section-title">Powerful Features for Winning Strategies</div>', unsafe_allow_html=True)

    f1, f2, f3, f4 = st.columns(4)
    features = [
        ("🧠", "AI Strategist", "Langflow and Ollama generate race-engineer style strategy explanations."),
        ("📈", "Telemetry Analytics", "Analyze lap pace, tyre life, stint patterns, and compound behavior."),
        ("⚡", "Real-Time Prediction", "Machine learning predicts pit stop decisions from race conditions."),
        ("🛡️", "Race Intelligence", "Support undercut, overcut, risk, and pit-window strategy reasoning."),
    ]

    for col, feature in zip([f1, f2, f3, f4], features):
        with col:
            st.markdown(
                f"""
                <div class="feature-card">
                    <h1>{feature[0]}</h1>
                    <h3>{feature[1]}</h3>
                    <p style="color:#94a3b8; line-height:1.7;">{feature[2]}</p>
                </div>
                """,
                unsafe_allow_html=True
            )


with tab_sim:
    st.markdown('<div class="section-title">AI Strategy Simulator</div>', unsafe_allow_html=True)

    sim_left, sim_right = st.columns([1, 1.35])

    with sim_left:
        st.markdown('<div class="panel">', unsafe_allow_html=True)

        driver = st.selectbox("Driver", drivers)
        lap_number = st.slider("Lap Number", 1, 100, 42)
        tyre_life = st.slider("Tyre Life", 1, 80, 25)
        stint = st.slider("Stint", 1, 10, 2)
        position = st.slider("Track Position", 1, 20, 3)

        compound = st.selectbox(
            "Tyre Compound",
            ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"],
            index=2
        )

        simulate = st.button("🏁 Run AI Strategy Simulation", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    with sim_right:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.subheader("AI Strategy Result")

        if simulate:
            payload = {
                "LapNumber": lap_number,
                "TyreLife": tyre_life,
                "Stint": stint,
                "Position": position,
                "Compound": compound,
                "Driver": driver
            }

            with st.spinner("Running ML model, Langflow agent, and Ollama strategist..."):
                response = requests.post(
                    f"{BASE_API}/predict-with-langflow-explanation",
                    json=payload,
                    timeout=180
                )

            if response.status_code == 200:
                result = response.json()

                pit_probability = result["probability_pit"] * 100
                stay_probability = result["probability_no_pit"] * 100

                if result["pit_stop_next_lap"] == 1:
                    recommendation = "PIT THIS LAP"
                    st.markdown('<div class="result-red">⚠ PIT WINDOW DETECTED</div>', unsafe_allow_html=True)
                else:
                    recommendation = "STAY OUT"
                    st.markdown('<div class="result-green">✓ CONTINUE CURRENT STINT</div>', unsafe_allow_html=True)

                a, b, c = st.columns(3)
                a.metric("Pit Probability", f"{pit_probability:.1f}%")
                b.metric("Stay Out", f"{stay_probability:.1f}%")
                c.metric("Recommendation", recommendation)

                st.markdown("### Strategy Recommendation Visualization")

                strategy_df = pd.DataFrame({
                    "Decision": ["Pit", "Stay Out"],
                    "Probability": [pit_probability, stay_probability]
                })

                fig_strategy = px.bar(
                    strategy_df,
                    x="Decision",
                    y="Probability",
                    color="Decision",
                    title="Pit Stop Recommendation Confidence"
                )

                st.plotly_chart(fig_strategy, use_container_width=True)

                explanation = result.get("ai_explanation") or result.get("explanation") or "No explanation returned."

                st.markdown(
                    f'<div class="ai-box">{explanation}</div>',
                    unsafe_allow_html=True
                )

                st.session_state.history.append({
                    "Driver": driver,
                    "Lap": lap_number,
                    "Compound": compound,
                    "Position": position,
                    "Recommendation": recommendation,
                    "Pit Probability": round(pit_probability, 1)
                })
            else:
                st.error(response.text)
        else:
            st.info("Configure race conditions and run the simulation.")

        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.history:

         st.markdown('<div class="section-title">Historical vs Predicted Strategy Comparison</div>', unsafe_allow_html=True)

         comparison_df = pd.DataFrame({
             "Metric": [
                 "Driver",
                 "Lap",
                 "Compound",
                 "Position",
                 "Historical Strategy",
                 "Predicted Strategy"
             ],
             "Historical": [
                 driver,
                 lap_number,
                 compound,
                 position,
                 "Stay Out",
                 ""
             ],
             "Predicted": [
                 driver,
                 lap_number,
                 compound,
                 position,
                 "",
                 recommendation
             ]
         })

         st.dataframe(comparison_df, use_container_width=True)

         fig_compare = px.bar(
             pd.DataFrame({
                 "Strategy": ["Historical", "Predicted"],
                 "Probability": [50, pit_probability]
             }),
             x="Strategy",
             y="Probability",
             title="Historical vs Predicted Strategy Confidence"
         )

         st.plotly_chart(fig_compare, use_container_width=True)

         st.divider()

    st.markdown('<div class="section-title">Simulation History</div>', unsafe_allow_html=True)
    
    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    else:
        st.info("No simulations executed yet.")


with tab_analytics:
    st.markdown('<div class="section-title">Interactive Race Analytics</div>', unsafe_allow_html=True)

    race_df = load_race_dataframe()

    if race_df is None:
        st.error("Race data CSV not found. Please check data/monaco_2024_race.csv or data/multi_race_2024_raw.csv")
    else:
        st.success("Race telemetry dataset loaded successfully.")

        st.markdown("### Dataset Preview")
        st.dataframe(race_df.head(), use_container_width=True)

        if "Driver" in race_df.columns:
            drivers_from_data = sorted(race_df["Driver"].dropna().unique())
        else:
            drivers_from_data = drivers

        selected_driver = st.selectbox("Select Driver for Analytics", drivers_from_data)

        st.markdown("### Dynamic Telemetry Filters")

        filter_col1, filter_col2, filter_col3 = st.columns([1, 1, 1])

        with filter_col1:
            compound_filter = st.multiselect(
                "Tyre Compound",
                options=sorted(race_df["Compound"].dropna().unique())
                if "Compound" in race_df.columns else [],
                default=sorted(race_df["Compound"].dropna().unique())
                if "Compound" in race_df.columns else []
            )

        with filter_col2:
            stint_filter = st.multiselect(
                "Stint",
                options=sorted(race_df["Stint"].dropna().unique())
                if "Stint" in race_df.columns else [],
                default=sorted(race_df["Stint"].dropna().unique())
                if "Stint" in race_df.columns else []
            )

        with filter_col3:
            if "LapNumber" in race_df.columns:
                lap_range = st.slider(
                "Lap Range",
                int(race_df["LapNumber"].min()),
                int(race_df["LapNumber"].max()),
                (
                    int(race_df["LapNumber"].min()),
                    int(race_df["LapNumber"].max())
                )
            )

        st.divider()

        if "Driver" in race_df.columns:
            driver_df = race_df[race_df["Driver"] == selected_driver].copy()
        else:
            driver_df = race_df.copy()

        if "Compound" in driver_df.columns:
            driver_df = driver_df[
                driver_df["Compound"].isin(compound_filter)
            ]

        if "Stint" in driver_df.columns:
            driver_df = driver_df[
                driver_df["Stint"].isin(stint_filter)
            ]

        if "LapNumber" in driver_df.columns:
            driver_df = driver_df[
                (driver_df["LapNumber"] >= lap_range[0]) &
                (driver_df["LapNumber"] <= lap_range[1])
            ]

        if "LapTimeSeconds" in driver_df.columns:
            c1.metric("Average Lap", f"{driver_df['LapTimeSeconds'].mean():.2f}s")
            c2.metric("Fastest Lap", f"{driver_df['LapTimeSeconds'].min():.2f}s")
            c3.metric("Slowest Lap", f"{driver_df['LapTimeSeconds'].max():.2f}s")
        else:
            c1.metric("Average Lap", "N/A")
            c2.metric("Fastest Lap", "N/A")
            c3.metric("Slowest Lap", "N/A")

        if "Stint" in driver_df.columns:
            c4.metric("Total Stints", driver_df["Stint"].nunique())
        else:
            c4.metric("Total Stints", "N/A")

        st.markdown("### Lap Time Trend")

        if "LapNumber" in driver_df.columns and "LapTimeSeconds" in driver_df.columns:
            fig_lap = px.line(
                driver_df,
                x="LapNumber",
                y="LapTimeSeconds",
                color="Compound" if "Compound" in driver_df.columns else None,
                markers=True,
                title=f"Lap Time Trend - {selected_driver}"
            )
            st.plotly_chart(fig_lap, use_container_width=True)
        else:
            st.warning("LapNumber or LapTimeSeconds column missing.")

        st.markdown("### Tyre Compound Usage")

        if "Compound" in driver_df.columns:
            compound_usage = driver_df["Compound"].value_counts().reset_index()
            compound_usage.columns = ["Compound", "Laps"]

            fig_compound = px.bar(
                compound_usage,
                x="Compound",
                y="Laps",
                title=f"Tyre Compound Usage - {selected_driver}"
            )
            st.plotly_chart(fig_compound, use_container_width=True)
        else:
            st.warning("Compound column missing.")

        st.markdown("### Tyre Life Trend")

        if "LapNumber" in driver_df.columns and "TyreLife" in driver_df.columns:
            fig_tyre = px.line(
                driver_df,
                x="LapNumber",
                y="TyreLife",
                color="Compound" if "Compound" in driver_df.columns else None,
                markers=True,
                title=f"Tyre Life Trend - {selected_driver}"
            )
            st.plotly_chart(fig_tyre, use_container_width=True)
        else:
            st.warning("LapNumber or TyreLife column missing.")

        st.markdown("### Race Position Trend")

        if "LapNumber" in driver_df.columns and "Position" in driver_df.columns:
            fig_pos = px.line(
                driver_df,
                x="LapNumber",
                y="Position",
                markers=True,
                title=f"Race Position Trend - {selected_driver}"
            )
            fig_pos.update_yaxes(autorange="reversed")
            st.plotly_chart(fig_pos, use_container_width=True)
        else:
            st.warning("LapNumber or Position column missing.")

        st.markdown("### Stint Summary")

        if "Stint" in driver_df.columns:
            summary_cols = {}

            if "LapNumber" in driver_df.columns:
                summary_cols["Total Laps"] = ("LapNumber", "count")

            if "LapTimeSeconds" in driver_df.columns:
                summary_cols["Average Lap Time"] = ("LapTimeSeconds", "mean")

            if "TyreLife" in driver_df.columns:
                summary_cols["Max Tyre Life"] = ("TyreLife", "max")

            if summary_cols:
                stint_summary = driver_df.groupby("Stint").agg(**summary_cols).reset_index()
                st.dataframe(stint_summary, use_container_width=True)
            else:
                st.warning("No valid columns available for stint summary.")
        else:
            st.warning("Stint column missing.")

        st.markdown('<div class="section-title">Driver Strategy Comparison</div>', unsafe_allow_html=True)

        dcol1, dcol2 = st.columns(2)

        driver_1 = dcol1.selectbox("Driver 1", drivers_from_data, index=0)
        driver_2 = dcol2.selectbox(
            "Driver 2",
            drivers_from_data,
            index=1 if len(drivers_from_data) > 1 else 0
        )

        if "Driver" in race_df.columns:
            compare_df = race_df[race_df["Driver"].isin([driver_1, driver_2])].copy()
            driver_1_df = race_df[race_df["Driver"] == driver_1].copy()
            driver_2_df = race_df[race_df["Driver"] == driver_2].copy()
        else:
            compare_df = race_df.copy()
            driver_1_df = race_df.copy()
            driver_2_df = race_df.copy()

        st.markdown("### Lap Time Comparison")

        if "LapNumber" in compare_df.columns and "LapTimeSeconds" in compare_df.columns and "Driver" in compare_df.columns:
            fig_compare = px.line(
                compare_df,
                x="LapNumber",
                y="LapTimeSeconds",
                color="Driver",
                markers=True,
                title=f"Lap Time Comparison: {driver_1} vs {driver_2}"
            )
            st.plotly_chart(fig_compare, use_container_width=True)
        else:
            st.warning("Required columns missing for lap time comparison.")

        st.markdown("### Strategy Metrics Comparison")

        m1, m2 = st.columns(2)

        with m1:
            st.markdown(f"#### {driver_1}")

            if "LapTimeSeconds" in driver_1_df.columns:
                st.metric("Average Lap Time", f"{driver_1_df['LapTimeSeconds'].mean():.2f}s")
                st.metric("Fastest Lap", f"{driver_1_df['LapTimeSeconds'].min():.2f}s")
                st.metric("Slowest Lap", f"{driver_1_df['LapTimeSeconds'].max():.2f}s")

            if "Stint" in driver_1_df.columns:
                st.metric("Total Stints", driver_1_df["Stint"].nunique())

            if "Compound" in driver_1_df.columns:
                compounds_1 = ", ".join(driver_1_df["Compound"].dropna().unique())
                st.write(f"**Compounds Used:** {compounds_1}")

        with m2:
            st.markdown(f"#### {driver_2}")

            if "LapTimeSeconds" in driver_2_df.columns:
                st.metric("Average Lap Time", f"{driver_2_df['LapTimeSeconds'].mean():.2f}s")
                st.metric("Fastest Lap", f"{driver_2_df['LapTimeSeconds'].min():.2f}s")
                st.metric("Slowest Lap", f"{driver_2_df['LapTimeSeconds'].max():.2f}s")

            if "Stint" in driver_2_df.columns:
                st.metric("Total Stints", driver_2_df["Stint"].nunique())

            if "Compound" in driver_2_df.columns:
                compounds_2 = ", ".join(driver_2_df["Compound"].dropna().unique())
                st.write(f"**Compounds Used:** {compounds_2}")

        st.markdown("### Tyre Compound Strategy Comparison")

        if "Compound" in compare_df.columns and "Driver" in compare_df.columns:
            compound_compare = (
                compare_df
                .groupby(["Driver", "Compound"])
                .size()
                .reset_index(name="Laps")
            )

            fig_compound_compare = px.bar(
                compound_compare,
                x="Compound",
                y="Laps",
                color="Driver",
                barmode="group",
                title=f"Tyre Compound Usage: {driver_1} vs {driver_2}"
            )
            st.plotly_chart(fig_compound_compare, use_container_width=True)
        else:
            st.warning("Required columns missing for compound comparison.")

        st.markdown("### Stint Strategy Comparison")

        if "Stint" in compare_df.columns and "Driver" in compare_df.columns and "LapNumber" in compare_df.columns:
            stint_compare = (
                compare_df
                .groupby(["Driver", "Stint"])
                .agg(
                    Total_Laps=("LapNumber", "count"),
                    Avg_Lap_Time=("LapTimeSeconds", "mean")
                )
                .reset_index()
            )

            st.dataframe(stint_compare, use_container_width=True)

            fig_stint_compare = px.bar(
                stint_compare,
                x="Stint",
                y="Total_Laps",
                color="Driver",
                barmode="group",
                title=f"Stint Length Comparison: {driver_1} vs {driver_2}"
            )
            st.plotly_chart(fig_stint_compare, use_container_width=True)
        else:
            st.warning("Required columns missing for stint comparison.")


with tab_about:
    st.markdown('<div class="section-title">About PitSense AI</div>', unsafe_allow_html=True)
    st.markdown("""
    PitSense AI is an AI-powered Formula 1 strategy platform designed to analyze
    telemetry patterns and simulate pit stop decision-making.

    The platform combines:
    - FastF1 telemetry data
    - Machine learning pit stop prediction
    - FastAPI backend services
    - Streamlit frontend
    - Langflow orchestration
    - Ollama local LLM explanations
    - Docker-based deployment
    """)


with tab_docs:
    st.markdown('<div class="section-title">System Documentation</div>', unsafe_allow_html=True)

    st.code("""
FastF1 Telemetry
    ↓
Data Processing
    ↓
ML Prediction Model
    ↓
FastAPI Backend
    ↓
Langflow Agent
    ↓
Ollama LLM
    ↓
Streamlit Website
""")

    st.markdown("""
    ### Main API Endpoints

    - `/predict`
    - `/predict-with-explanation`
    - `/predict-with-langflow-explanation`
    - `/analytics/summary`
    - `/analytics/drivers`
    - `/analytics/driver/{driver}`
    """)


st.markdown("""
<hr>
<p style="text-align:center; color:#64748b; font-size:13px;">
PitSense AI — Formula 1 Strategy Intelligence Platform<br>
FastAPI • Streamlit • Langflow • Ollama • Scikit-learn • Docker
</p>
""", unsafe_allow_html=True)