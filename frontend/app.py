import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="PitSense AI",
    page_icon="🏎️",
    layout="wide"
)

BASE_API = "http://backend:8000"

if "history" not in st.session_state:
    st.session_state.history = []


st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at top left, rgba(255, 30, 0, 0.28), transparent 35%),
        radial-gradient(circle at bottom right, rgba(120, 0, 0, 0.35), transparent 40%),
        linear-gradient(135deg, #020202 0%, #080808 45%, #190000 100%);
    color: white;
}

.main-title {
    font-size: 64px;
    font-weight: 1000;
    color: #ff1e00;
    text-align: center;
    letter-spacing: 4px;
    text-shadow: 0 0 22px rgba(255,30,0,0.9);
}

.subtitle {
    text-align: center;
    color: #e5e7eb;
    font-size: 21px;
    margin-bottom: 25px;
}

.race-banner {
    background: linear-gradient(90deg, #ff1e00, #111, #ff1e00);
    padding: 13px;
    border-radius: 14px;
    text-align: center;
    font-weight: 900;
    letter-spacing: 2px;
    margin-bottom: 25px;
}

.card {
    background: rgba(255, 255, 255, 0.065);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid rgba(255, 30, 0, 0.55);
    box-shadow: 0 0 30px rgba(255, 30, 0, 0.24);
}

.ai-card {
    background: rgba(0, 0, 0, 0.62);
    padding: 24px;
    border-radius: 20px;
    border-left: 8px solid #ff1e00;
    box-shadow: 0 0 30px rgba(255, 30, 0, 0.35);
    font-size: 17px;
    line-height: 1.65;
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

.status-box {
    padding: 18px;
    border-radius: 16px;
    background: rgba(255,255,255,0.07);
    border: 1px solid rgba(255,255,255,0.18);
    text-align: center;
    font-weight: 800;
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
    '<div class="subtitle">AI-Powered Formula 1 Pit Stop Strategy & Telemetry Intelligence Platform</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="race-banner">RACE CONTROL • ML PREDICTION • LANGFLOW AI STRATEGIST • OLLAMA LLM</div>',
    unsafe_allow_html=True
)


@st.cache_data(ttl=60)
def get_summary():
    return requests.get(f"{BASE_API}/analytics/summary", timeout=10).json()


@st.cache_data(ttl=60)
def get_drivers():
    return requests.get(f"{BASE_API}/analytics/drivers", timeout=10).json()["drivers"]


try:
    summary_data = get_summary()
    driver_list = get_drivers()
except Exception:
    st.error("Backend API is not available. Make sure FastAPI is running.")
    st.stop()


tab1, tab2, tab3 = st.tabs([
    "🏁 AI Strategy Simulator",
    "📊 Analytics",
    "⚔️ Driver Comparison"
])


with tab1:
    st.sidebar.title("🏁 Race Control Panel")

    lap_number = st.sidebar.slider("Lap Number", 1, 100, 42)
    tyre_life = st.sidebar.slider("Tyre Life", 1, 80, 25)
    stint = st.sidebar.slider("Stint", 1, 10, 2)
    position = st.sidebar.slider("Track Position", 1, 20, 3)

    compound = st.sidebar.selectbox(
        "Tyre Compound",
        ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"],
        index=2
    )

    driver = st.sidebar.selectbox("Driver", driver_list)

    col1, col2 = st.columns([1, 1.45])

    with col1:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🏎️ Race Simulation Inputs")
        st.write(f"**Driver:** {driver}")
        st.write(f"**Lap:** {lap_number}")
        st.write(f"**Tyre Life:** {tyre_life} laps")
        st.write(f"**Stint:** {stint}")
        st.write(f"**Track Position:** P{position}")
        st.write(f"**Compound:** {compound}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### System Architecture")
        st.markdown("""
        ```text
        Streamlit UI
            ↓
        FastAPI Backend
            ↓
        ML Prediction Model
            ↓
        Langflow Agent
            ↓
        Ollama LLM
        ```
        """)

    with col2:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("🧠 AI Strategy Prediction Engine")

        if st.button("🚦 RUN AI STRATEGY SIMULATION", use_container_width=True):
            payload = {
                "LapNumber": lap_number,
                "TyreLife": tyre_life,
                "Stint": stint,
                "Position": position,
                "Compound": compound,
                "Driver": driver
            }

            with st.spinner("Running ML prediction and Langflow AI strategist..."):
                try:
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
                            decision = "PIT"
                            st.markdown(
                                '<div class="result-bad">⚠️ BOX NOW — PIT STOP WINDOW DETECTED</div>',
                                unsafe_allow_html=True
                            )
                        else:
                            decision = "STAY OUT"
                            st.markdown(
                                '<div class="result-good">✅ STAY OUT — CONTINUE CURRENT STINT</div>',
                                unsafe_allow_html=True
                            )

                        m1, m2, m3 = st.columns(3)

                        with m1:
                            st.metric("Pit Probability", f"{pit_probability:.1f}%")

                        with m2:
                            st.metric("Stay Out Probability", f"{stay_probability:.1f}%")

                        with m3:
                            st.metric("AI Decision", decision)

                        st.subheader("📊 Pit Window Confidence")
                        st.progress(min(int(pit_probability), 100) / 100)

                        if pit_probability >= 70:
                            st.warning("High pit-window pressure. Prepare pit crew and evaluate undercut opportunity.")
                        elif pit_probability >= 40:
                            st.info("Medium strategy pressure. Continue monitoring degradation and traffic.")
                        else:
                            st.success("Low immediate pit pressure. Track position preservation is preferred.")

                        st.subheader("🤖 Langflow AI Race Strategist")
                        st.markdown(
                            f'<div class="ai-card">{result["ai_explanation"]}</div>',
                            unsafe_allow_html=True
                        )

                        st.session_state.history.append({
                            "Driver": driver,
                            "Lap": lap_number,
                            "TyreLife": tyre_life,
                            "Compound": compound,
                            "Position": position,
                            "Prediction": decision,
                            "PitProbability": round(pit_probability, 1),
                            "AI": "Langflow + Ollama"
                        })

                    else:
                        st.error(f"Prediction failed: {response.text}")

                except Exception as e:
                    st.error(f"Could not connect to AI strategy backend: {e}")

        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()
    st.subheader("📜 AI Strategy Simulation History")

    if st.session_state.history:
        st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
    else:
        st.info("No AI strategy simulations executed yet.")


with tab2:
    st.subheader("📊 Platform Analytics")

    metric1, metric2, metric3, metric4 = st.columns(4)

    with metric1:
        st.metric("Telemetry Records", summary_data["total_records"])

    with metric2:
        st.metric("Drivers", summary_data["total_drivers"])

    with metric3:
        st.metric("Compounds", summary_data["total_compounds"])

    with metric4:
        st.metric("Avg Lap Time", f"{summary_data['average_lap_time']:.2f}s")

    st.divider()

    selected_driver = st.selectbox("Select Driver Analytics", driver_list)

    try:
        driver_data = requests.get(
            f"{BASE_API}/analytics/driver/{selected_driver}",
            timeout=10
        ).json()

        analytics_col1, analytics_col2 = st.columns(2)

        with analytics_col1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(f"{selected_driver} Performance")
            st.metric("Average Lap Time", f"{driver_data['average_lap_time']:.2f}s")
            st.metric("Fastest Lap", f"{driver_data['fastest_lap_time']:.2f}s")
            st.metric("Slowest Lap", f"{driver_data['slowest_lap_time']:.2f}s")
            st.metric("Total Laps", driver_data["total_laps"])
            st.markdown("</div>", unsafe_allow_html=True)

        with analytics_col2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader("Tyre Strategy")
            st.metric("Total Stints", driver_data["stints"])
            st.write("**Compounds Used:**")
            for compound_used in driver_data["compounds_used"]:
                st.write(f"• {compound_used}")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception:
        st.error("Could not load driver analytics.")


with tab3:
    st.subheader("⚔️ Driver Strategy Comparison")

    compare_col1, compare_col2 = st.columns(2)

    driver_1 = compare_col1.selectbox("Driver 1", driver_list, index=0)
    driver_2 = compare_col2.selectbox(
        "Driver 2",
        driver_list,
        index=1 if len(driver_list) > 1 else 0
    )

    try:
        d1 = requests.get(f"{BASE_API}/analytics/driver/{driver_1}", timeout=10).json()
        d2 = requests.get(f"{BASE_API}/analytics/driver/{driver_2}", timeout=10).json()

        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(driver_1)
            st.metric("Average Lap", f"{d1['average_lap_time']:.2f}s")
            st.metric("Fastest Lap", f"{d1['fastest_lap_time']:.2f}s")
            st.metric("Stints", d1["stints"])
            st.write("Compounds:", ", ".join(d1["compounds_used"]))
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="card">', unsafe_allow_html=True)
            st.subheader(driver_2)
            st.metric("Average Lap", f"{d2['average_lap_time']:.2f}s")
            st.metric("Fastest Lap", f"{d2['fastest_lap_time']:.2f}s")
            st.metric("Stints", d2["stints"])
            st.write("Compounds:", ", ".join(d2["compounds_used"]))
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception:
        st.error("Could not load driver comparison.")