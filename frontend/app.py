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

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at top left, rgba(255,0,0,0.20), transparent 25%),
        radial-gradient(circle at bottom right, rgba(120,0,0,0.25), transparent 35%),
        linear-gradient(135deg, #020202 0%, #070707 50%, #140000 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    background: #040404;
    border-right: 1px solid rgba(255,0,0,0.25);
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 5px;
    margin-bottom: 20px;
}

.logo {
    font-size: 32px;
    font-weight: 900;
    color: #ff2200;
    text-shadow: 0 0 20px rgba(255,0,0,0.8);
}

.nav-links {
    color: #ddd;
    font-size: 15px;
}

.hero {
    padding: 80px 40px;
    border-radius: 28px;
    background:
        linear-gradient(135deg, rgba(255,0,0,0.18), rgba(0,0,0,0.65));
    border: 1px solid rgba(255,0,0,0.25);
    box-shadow: 0 0 50px rgba(255,0,0,0.18);
}

.hero-title {
    font-size: 74px;
    font-weight: 1000;
    color: white;
    line-height: 1.05;
}

.hero-highlight {
    color: #ff2200;
    text-shadow: 0 0 25px rgba(255,0,0,0.9);
}

.hero-subtitle {
    font-size: 21px;
    color: #d1d5db;
    margin-top: 20px;
    line-height: 1.6;
}

.hero-buttons {
    margin-top: 30px;
}

.metric-card {
    background: rgba(255,255,255,0.05);
    padding: 30px;
    border-radius: 24px;
    border: 1px solid rgba(255,0,0,0.18);
    text-align: center;
    box-shadow: 0 0 25px rgba(255,0,0,0.08);
}

.metric-value {
    font-size: 42px;
    font-weight: 900;
    color: #ff2200;
}

.metric-label {
    color: #d1d5db;
    margin-top: 10px;
}

.section-title {
    font-size: 44px;
    font-weight: 900;
    margin-top: 70px;
    margin-bottom: 20px;
}

.glass-card {
    background: rgba(255,255,255,0.04);
    border-radius: 24px;
    padding: 30px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(12px);
}

.feature-card {
    background: rgba(255,255,255,0.04);
    border-radius: 24px;
    padding: 30px;
    border: 1px solid rgba(255,0,0,0.15);
    height: 100%;
}

.feature-title {
    font-size: 24px;
    font-weight: 800;
    margin-top: 15px;
}

.feature-text {
    color: #d1d5db;
    margin-top: 10px;
    line-height: 1.7;
}

.ai-box {
    background: rgba(0,0,0,0.55);
    border-left: 6px solid #ff2200;
    padding: 25px;
    border-radius: 20px;
    margin-top: 20px;
    line-height: 1.7;
}

.footer {
    text-align: center;
    padding: 50px 20px;
    color: #9ca3af;
    margin-top: 60px;
}

.stButton > button {
    background: linear-gradient(90deg, #ff2200, #c40000);
    border: none;
    color: white;
    border-radius: 14px;
    height: 3.2rem;
    font-weight: 800;
    width: 100%;
}

.stButton > button:hover {
    box-shadow: 0 0 30px rgba(255,0,0,0.8);
}

</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)
def get_summary():
    return requests.get(f"{BASE_API}/analytics/summary").json()


@st.cache_data(ttl=60)
def get_drivers():
    return requests.get(f"{BASE_API}/analytics/drivers").json()["drivers"]


summary = get_summary()
drivers = get_drivers()


st.markdown("""
<div class="navbar">
    <div class="logo">🏎️ PitSense AI</div>
    <div class="nav-links">
        AI Strategy Platform • Telemetry Intelligence • Formula 1 Analytics
    </div>
</div>
""", unsafe_allow_html=True)


hero_left, hero_right = st.columns([1.3, 1])

with hero_left:

    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            The Future of<br>
            <span class="hero-highlight">
            Formula 1 Strategy Intelligence
            </span>
        </div>

        <div class="hero-subtitle">
            PitSense AI combines machine learning, telemetry analytics,
            Langflow orchestration, and local LLM intelligence to simulate
            professional Formula 1 pit stop strategy decisions in real time.
        </div>
    </div>
    """, unsafe_allow_html=True)

with hero_right:

    st.image(
        "https://images.unsplash.com/photo-1503376780353-7e6692767b70?q=80&w=1400&auto=format&fit=crop",
        use_container_width=True
    )


st.markdown(
    '<div class="section-title">Platform Metrics</div>',
    unsafe_allow_html=True
)

m1, m2, m3, m4 = st.columns(4)

metrics = [
    ("Telemetry Records", summary["total_records"]),
    ("Drivers", summary["total_drivers"]),
    ("Compounds", summary["total_compounds"]),
    ("Avg Lap Time", f"{summary['average_lap_time']:.2f}s")
]

for col, metric in zip([m1, m2, m3, m4], metrics):

    with col:

        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{metric[1]}</div>
            <div class="metric-label">{metric[0]}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown(
    '<div class="section-title">AI Strategy Simulator</div>',
    unsafe_allow_html=True
)

sim_col1, sim_col2 = st.columns([1, 1.5])

with sim_col1:

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    lap_number = st.slider("Lap Number", 1, 100, 42)
    tyre_life = st.slider("Tyre Life", 1, 80, 25)
    stint = st.slider("Stint", 1, 10, 2)
    position = st.slider("Track Position", 1, 20, 3)

    compound = st.selectbox(
        "Tyre Compound",
        ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]
    )

    driver = st.selectbox("Driver", drivers)

    simulate = st.button("🚦 Run AI Strategy Simulation")

    st.markdown('</div>', unsafe_allow_html=True)

with sim_col2:

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    st.subheader("🧠 AI Race Strategist")

    if simulate:

        payload = {
            "LapNumber": lap_number,
            "TyreLife": tyre_life,
            "Stint": stint,
            "Position": position,
            "Compound": compound,
            "Driver": driver
        }

        with st.spinner("Running AI race strategy engine..."):

            response = requests.post(
                f"{BASE_API}/predict-with-langflow-explanation",
                json=payload,
                timeout=180
            )

            result = response.json()

            pit_probability = result["probability_pit"] * 100
            stay_probability = result["probability_no_pit"] * 100

            if result["pit_stop_next_lap"] == 1:

                st.error("⚠️ PIT WINDOW DETECTED")

            else:

                st.success("✅ STAY OUT — CONTINUE CURRENT STINT")

            r1, r2, r3 = st.columns(3)

            r1.metric(
                "Pit Probability",
                f"{pit_probability:.1f}%"
            )

            r2.metric(
                "Stay Out",
                f"{stay_probability:.1f}%"
            )

            r3.metric(
                "Driver",
                driver
            )

            st.markdown(f"""
            <div class="ai-box">
            {result["ai_explanation"]}
            </div>
            """, unsafe_allow_html=True)

            st.session_state.history.append({
                "Driver": driver,
                "Lap": lap_number,
                "Compound": compound,
                "Pit Probability": round(pit_probability, 1)
            })

    else:

        st.info("""
        Run a simulation to generate:
        - AI pit strategy
        - tyre degradation analysis
        - pit window reasoning
        - race strategy recommendations
        """)

    st.markdown('</div>', unsafe_allow_html=True)


st.markdown(
    '<div class="section-title">Core Platform Features</div>',
    unsafe_allow_html=True
)

f1, f2, f3 = st.columns(3)

features = [
    (
        "🧠",
        "AI Strategy Agent",
        "Langflow + Ollama powered strategy explanations with real-time telemetry interpretation."
    ),
    (
        "📊",
        "Telemetry Analytics",
        "Analyze tyre degradation, lap performance, and race strategy evolution."
    ),
    (
        "⚡",
        "Real-Time Predictions",
        "Machine learning pipeline predicts pit-stop decisions using race telemetry."
    )
]

for col, feature in zip([f1, f2, f3], features):

    with col:

        st.markdown(f"""
        <div class="feature-card">
            <div style="font-size:48px;">{feature[0]}</div>
            <div class="feature-title">{feature[1]}</div>
            <div class="feature-text">{feature[2]}</div>
        </div>
        """, unsafe_allow_html=True)


st.markdown(
    '<div class="section-title">Simulation History</div>',
    unsafe_allow_html=True
)

if st.session_state.history:

    st.dataframe(
        pd.DataFrame(st.session_state.history),
        use_container_width=True
    )

else:

    st.info("No simulations executed yet.")


st.markdown("""
<div class="footer">
    PitSense AI • Formula 1 Telemetry Intelligence Platform<br>
    Powered by FastAPI • Streamlit • Langflow • Ollama • Scikit-learn
</div>
""", unsafe_allow_html=True)