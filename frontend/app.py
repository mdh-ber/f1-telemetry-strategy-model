import streamlit as st
import requests
import pandas as pd

st.set_page_config(
    page_title="PitSense AI",
    page_icon="🏁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

BASE_API = "http://backend:8000"

if "history" not in st.session_state:
    st.session_state.history = []


@st.cache_data(ttl=60)
def get_summary():
    return requests.get(f"{BASE_API}/analytics/summary", timeout=10).json()


@st.cache_data(ttl=60)
def get_drivers():
    return requests.get(f"{BASE_API}/analytics/drivers", timeout=10).json()["drivers"]


try:
    summary = get_summary()
    drivers = get_drivers()
except Exception:
    st.error("Backend API is not available. Start Docker Compose and make sure FastAPI is running.")
    st.stop()


st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background:
        radial-gradient(circle at 70% 20%, rgba(255, 36, 24, 0.18), transparent 35%),
        linear-gradient(135deg, #03070d 0%, #070b12 45%, #070707 100%);
    color: white;
}

.block-container {
    padding-top: 1.2rem;
    max-width: 1280px;
}

.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 18px 4px 24px 4px;
    border-bottom: 1px solid rgba(255,255,255,0.08);
}

.brand {
    display: flex;
    align-items: center;
    gap: 18px;
}

.f1-mark {
    color: #ff1e00;
    font-size: 34px;
    font-weight: 1000;
    letter-spacing: -3px;
    border-right: 1px solid rgba(255,255,255,0.28);
    padding-right: 20px;
}

.brand-name {
    font-size: 24px;
    font-weight: 900;
    letter-spacing: 1px;
}

.brand-name span {
    color: #ff1e00;
}

.nav-links {
    display: flex;
    gap: 34px;
    font-size: 13px;
    font-weight: 800;
    color: #e5e7eb;
    letter-spacing: 1px;
}

.nav-button {
    border: 1px solid #ff1e00;
    padding: 12px 22px;
    border-radius: 8px;
    color: white;
}

.hero {
    margin-top: 42px;
    display: grid;
    grid-template-columns: 1.05fr 1fr;
    gap: 42px;
    align-items: center;
}

.kicker {
    color: #ff1e00;
    font-size: 14px;
    font-weight: 900;
    letter-spacing: 1.8px;
    margin-bottom: 18px;
}

.hero-title {
    font-size: 64px;
    line-height: 0.98;
    font-weight: 1000;
    letter-spacing: -2px;
}

.hero-title span {
    color: #ff1e00;
}

.hero-text {
    color: #cbd5e1;
    font-size: 17px;
    line-height: 1.8;
    max-width: 560px;
    margin-top: 24px;
}

.hero-actions {
    display: flex;
    gap: 18px;
    margin-top: 32px;
}

.primary-btn {
    background: linear-gradient(90deg, #ff1e00, #c90000);
    padding: 16px 28px;
    border-radius: 8px;
    font-weight: 900;
    color: white;
    display: inline-block;
}

.secondary-btn {
    border: 1px solid rgba(255,255,255,0.55);
    padding: 16px 28px;
    border-radius: 8px;
    font-weight: 900;
    color: white;
    display: inline-block;
}

.hero-visual {
    height: 420px;
    border-radius: 24px;
    background:
        linear-gradient(90deg, rgba(3,7,13,0.15), rgba(3,7,13,0.96)),
        url("https://images.unsplash.com/photo-1558611848-73f7eb4001a1?q=80&w=1400&auto=format&fit=crop");
    background-size: cover;
    background-position: center;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0 0 60px rgba(255, 30, 0, 0.15);
}

.feature-strip {
    display: flex;
    gap: 42px;
    margin-top: 40px;
    color: #cbd5e1;
    font-size: 13px;
    font-weight: 800;
}

.metrics {
    margin-top: 52px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 18px;
}

.metric-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 14px;
    padding: 26px;
}

.metric-value {
    font-size: 34px;
    font-weight: 900;
}

.metric-label {
    color: #94a3b8;
    font-size: 13px;
    margin-top: 6px;
}

.section {
    margin-top: 70px;
    padding: 34px;
    background: rgba(255,255,255,0.025);
    border: 1px solid rgba(255,255,255,0.09);
    border-radius: 22px;
}

.section-center {
    text-align: center;
}

.section-kicker {
    color: #ff1e00;
    font-weight: 900;
    font-size: 13px;
    letter-spacing: 1.6px;
}

.section-title {
    font-size: 34px;
    font-weight: 900;
    margin-top: 8px;
}

.section-subtitle {
    color: #94a3b8;
    margin-top: 8px;
}

.panel {
    background: rgba(8, 13, 22, 0.92);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 26px;
    height: 100%;
}

.result-box-red {
    background: rgba(255, 30, 0, 0.15);
    border: 1px solid rgba(255, 30, 0, 0.5);
    border-radius: 12px;
    padding: 22px;
    color: #ff4b3e;
    font-weight: 900;
    font-size: 18px;
}

.result-box-green {
    background: rgba(0, 180, 100, 0.14);
    border: 1px solid rgba(0, 255, 136, 0.45);
    border-radius: 12px;
    padding: 22px;
    color: #00ff88;
    font-weight: 900;
    font-size: 18px;
}

.ai-box {
    border-left: 4px solid #ff1e00;
    padding: 18px 20px;
    background: rgba(0,0,0,0.35);
    border-radius: 8px;
    color: #dbeafe;
    line-height: 1.7;
    margin-top: 18px;
}

.features-grid {
    margin-top: 34px;
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 22px;
}

.feature-card {
    background: rgba(255,255,255,0.035);
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 16px;
    padding: 26px;
}

.feature-icon {
    font-size: 34px;
    color: #ff1e00;
}

.feature-heading {
    margin-top: 18px;
    font-size: 17px;
    font-weight: 900;
}

.feature-copy {
    color: #94a3b8;
    margin-top: 10px;
    line-height: 1.7;
    font-size: 14px;
}

.footer {
    text-align: center;
    color: #64748b;
    padding: 48px 0 20px 0;
    font-size: 13px;
}

.stButton > button {
    background: linear-gradient(90deg, #ff1e00, #d60000);
    color: white;
    border: none;
    height: 3.2rem;
    font-weight: 900;
    border-radius: 9px;
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
<div class="navbar">
    <div class="brand">
        <div class="f1-mark">F1</div>
        <div class="brand-name">PITSENSE <span>AI</span></div>
    </div>
    <div class="nav-links">
        <div>HOME</div>
        <div>FEATURES</div>
        <div>SIMULATOR</div>
        <div>ANALYTICS</div>
        <div class="nav-button">DOCUMENTATION</div>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="hero">
    <div>
        <div class="kicker">AI-POWERED F1 STRATEGY PLATFORM</div>
        <div class="hero-title">
            INTELLIGENT STRATEGY.<br>
            <span>FASTER DECISIONS.</span><br>
            RACE AHEAD.
        </div>
        <div class="hero-text">
            PitSense AI analyzes race telemetry, tyre conditions, stint behavior, 
            and machine learning predictions to support faster pit stop strategy 
            decisions with AI-generated race engineer explanations.
        </div>
        <div class="hero-actions">
            <div class="primary-btn">TRY AI SIMULATOR →</div>
            <div class="secondary-btn">EXPLORE ANALYTICS</div>
        </div>
        <div class="feature-strip">
            <div>▦ MACHINE LEARNING</div>
            <div>⌁ TELEMETRY ANALYTICS</div>
            <div>✦ AI STRATEGIST</div>
            <div>◉ REAL-TIME INSIGHTS</div>
        </div>
    </div>
    <div class="hero-visual"></div>
</div>
""", unsafe_allow_html=True)


st.markdown(f"""
<div class="metrics">
    <div class="metric-card">
        <div class="metric-value">{summary["total_records"]}</div>
        <div class="metric-label">Telemetry Records</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{summary["total_drivers"]}</div>
        <div class="metric-label">Drivers</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{summary["total_compounds"]}</div>
        <div class="metric-label">Tyre Compounds</div>
    </div>
    <div class="metric-card">
        <div class="metric-value">{summary["average_lap_time"]:.2f}s</div>
        <div class="metric-label">Average Lap Time</div>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="section section-center">
    <div class="section-kicker">AI STRATEGY SIMULATOR</div>
    <div class="section-title">Simulate. Analyze. Win.</div>
    <div class="section-subtitle">
        Configure race conditions and generate AI-powered pit stop strategy insights in real time.
    </div>
</div>
""", unsafe_allow_html=True)


sim_left, sim_right = st.columns([1, 1.35])

with sim_left:
    st.markdown('<div class="panel">', unsafe_allow_html=True)

    driver = st.selectbox("DRIVER", drivers)
    lap_number = st.slider("LAP NUMBER", 1, 100, 42)
    tyre_life = st.slider("TYRE LIFE (LAPS)", 1, 80, 25)
    stint = st.slider("STINT", 1, 10, 2)

    compound = st.selectbox(
        "TYRE COMPOUND",
        ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"],
        index=2
    )

    position = st.slider("TRACK POSITION", 1, 20, 3)

    simulate = st.button("🏁 RUN AI STRATEGY SIMULATION", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

with sim_right:
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("### AI STRATEGY RESULT")

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
                        decision = "PIT THIS LAP"
                        st.markdown(
                            '<div class="result-box-red">⚠ PIT WINDOW DETECTED</div>',
                            unsafe_allow_html=True
                        )
                    else:
                        decision = "STAY OUT"
                        st.markdown(
                            '<div class="result-box-green">✓ CONTINUE CURRENT STINT</div>',
                            unsafe_allow_html=True
                        )

                    c1, c2, c3 = st.columns(3)
                    c1.metric("Pit Probability", f"{pit_probability:.1f}%")
                    c2.metric("Stay Out Probability", f"{stay_probability:.1f}%")
                    c3.metric("Recommendation", decision)

                    st.markdown(
                        f'<div class="ai-box">{result["ai_explanation"]}</div>',
                        unsafe_allow_html=True
                    )

                    st.session_state.history.append({
                        "Driver": driver,
                        "Lap": lap_number,
                        "Compound": compound,
                        "Position": position,
                        "Recommendation": decision,
                        "Pit Probability": round(pit_probability, 1)
                    })
                else:
                    st.error(response.text)

            except Exception as e:
                st.error(f"Could not connect to AI strategy backend: {e}")
    else:
        st.info("Run the simulator to generate ML prediction and AI race strategist explanation.")

    st.markdown("</div>", unsafe_allow_html=True)


st.markdown("""
<div class="section section-center">
    <div class="section-kicker">BUILT FOR PERFORMANCE</div>
    <div class="section-title">Powerful Features for Winning Strategies</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="features-grid">
    <div class="feature-card">
        <div class="feature-icon">🧠</div>
        <div class="feature-heading">AI Strategist</div>
        <div class="feature-copy">
            Langflow and Ollama generate professional race engineer style strategy explanations.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">📈</div>
        <div class="feature-heading">Telemetry Analytics</div>
        <div class="feature-copy">
            Analyze lap pace, tyre life, stint patterns, and race performance signals.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">⚡</div>
        <div class="feature-heading">Real-Time Prediction</div>
        <div class="feature-copy">
            Machine learning predicts pit stop decisions from structured race conditions.
        </div>
    </div>
    <div class="feature-card">
        <div class="feature-icon">🛡️</div>
        <div class="feature-heading">Race Intelligence</div>
        <div class="feature-copy">
            Support undercut, overcut, risk, and pit-window reasoning in one platform.
        </div>
    </div>
</div>
""", unsafe_allow_html=True)


st.markdown("""
<div class="section">
    <div class="section-title">Simulation History</div>
</div>
""", unsafe_allow_html=True)

if st.session_state.history:
    st.dataframe(pd.DataFrame(st.session_state.history), use_container_width=True)
else:
    st.info("No simulations executed yet.")


st.markdown("""
<div class="footer">
    PitSense AI — Formula 1 Strategy Intelligence Platform<br>
    FastAPI • Streamlit • Langflow • Ollama • Scikit-learn • Docker
</div>
""", unsafe_allow_html=True)