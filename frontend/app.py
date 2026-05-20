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

st.markdown('<div class="race-banner">RACE CONTROL • STRATEGY WALL • PIT WINDOW SIMULATOR</div>', unsafe_allow_html=True)
 
st.sidebar.title("🏁 Race Control Panel")

st.sidebar.markdown("Configure live strategy conditions")
 
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
 
                if pit_probability >= 70:

                    st.warning("High pit stop risk detected. Strategy wall should prepare for boxing.")

                elif pit_probability >= 40:

                    st.info("Moderate pit stop possibility. Monitor tyre degradation and traffic.")

                else:

                    st.success("Low pit stop probability. Staying out is currently preferred.")
 
                st.subheader("🤖 AI Strategy Explanation")

                st.markdown(

                    f'<div class="explanation-box">{result["explanation"]}</div>',

                    unsafe_allow_html=True

                )
 
                comparison_df = pd.DataFrame({

                    "Parameter": [

                        "Driver",

                        "Lap",

                        "Tyre Life",

                        "Compound",

                        "Track Position",

                        "Prediction",

                        "Pit Probability"

                    ],

                    "Simulation Result": [

                        driver,

                        lap_number,

                        tyre_life,

                        compound,

                        position,

                        decision,

                        f"{pit_probability:.1f}%"

                    ]

                })
 
                st.subheader("⚔️ Historical vs Predicted Strategy")

                st.dataframe(comparison_df, use_container_width=True)
 
                st.session_state.history.append({

                    "Driver": driver,

                    "Lap": lap_number,

                    "TyreLife": tyre_life,

                    "Compound": compound,

                    "Position": position,

                    "Prediction": decision,

                    "PitProbability": round(pit_probability, 1),

                    "StayOutProbability": round(stay_probability, 1)

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
 
st.divider()
 
st.subheader("📈 Telemetry Analytics Dashboard")
 
try:

    telemetry_df = pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")
 
    analytics_col1, analytics_col2 = st.columns(2)
 
    with analytics_col1:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Driver Lap Pace Analysis")
 
        selected_driver = st.selectbox(

            "Select Driver",

            sorted(telemetry_df["Driver"].unique())

        )
 
        driver_df = telemetry_df[telemetry_df["Driver"] == selected_driver]
 
        lap_chart_df = driver_df[["LapNumber", "LapTimeSeconds"]].set_index("LapNumber")

        st.line_chart(lap_chart_df)
 
        st.markdown("</div>", unsafe_allow_html=True)
 
    with analytics_col2:

        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.subheader("Tyre Compound Usage")
 
        compound_counts = telemetry_df["Compound"].value_counts()

        st.bar_chart(compound_counts)
 
        st.markdown("</div>", unsafe_allow_html=True)
 
    st.divider()
 
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
 
    with metric_col1:

        st.metric("Total Laps", len(telemetry_df))
 
    with metric_col2:

        st.metric("Drivers", telemetry_df["Driver"].nunique())
 
    with metric_col3:

        st.metric("Compounds", telemetry_df["Compound"].nunique())
 
    with metric_col4:

        st.metric("Avg Lap Time", f"{telemetry_df['LapTimeSeconds'].mean():.2f}s")
 
except FileNotFoundError:

    st.warning("Telemetry dataset not found. Run the ML dataset creation script first.")
 