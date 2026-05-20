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

    background: linear-gradient(135deg, #050505 0%, #111827 45%, #1a0000 100%);

    color: white;

}
 
.main-title {

    font-size: 54px;

    font-weight: 900;

    color: #ff1e00;

    text-align: center;

    letter-spacing: 3px;

}
 
.subtitle {

    text-align: center;

    color: #d1d5db;

    font-size: 20px;

    margin-bottom: 30px;

}
 
.card {

    background: rgba(255, 255, 255, 0.07);

    padding: 25px;

    border-radius: 18px;

    border: 1px solid rgba(255, 30, 0, 0.5);

    box-shadow: 0 0 25px rgba(255, 30, 0, 0.25);

}
 
.result-good {

    background: linear-gradient(135deg, #003b1f, #006b3c);

    padding: 25px;

    border-radius: 18px;

    border: 1px solid #00ff88;

    font-size: 24px;

    font-weight: bold;

    text-align: center;

}
 
.result-bad {

    background: linear-gradient(135deg, #4b0000, #b00000);

    padding: 25px;

    border-radius: 18px;

    border: 1px solid #ff3333;

    font-size: 24px;

    font-weight: bold;

    text-align: center;

}
 
.explanation-box {

    background: rgba(0, 0, 0, 0.45);

    padding: 22px;

    border-radius: 16px;

    border-left: 6px solid #ff1e00;

    font-size: 17px;

    line-height: 1.6;

}
 
.compare-box {

    background: rgba(255,255,255,0.05);

    padding: 20px;

    border-radius: 15px;

    border: 1px solid #666;

}
 
[data-testid="stSidebar"] {

    background: #080808;

    border-right: 2px solid #ff1e00;

}
</style>

""", unsafe_allow_html=True)
 
st.markdown('<div class="main-title">🏎️ PitSense AI</div>', unsafe_allow_html=True)

st.markdown(

    '<div class="subtitle">Formula 1 Pit Stop Strategy Prediction System</div>',

    unsafe_allow_html=True

)
 
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
 
col1, col2 = st.columns([1, 1.3])
 
with col1:

    st.markdown('<div class="card">', unsafe_allow_html=True)
 
    st.subheader("Race Simulation Inputs")
 
    st.write(f"**Driver:** {driver}")

    st.write(f"**Current Lap:** {lap_number}")

    st.write(f"**Tyre Life:** {tyre_life} laps")

    st.write(f"**Current Stint:** {stint}")

    st.write(f"**Track Position:** P{position}")

    st.write(f"**Compound:** {compound}")
 
    st.markdown("</div>", unsafe_allow_html=True)
 
with col2:
 
    st.markdown('<div class="card">', unsafe_allow_html=True)
 
    st.subheader("Strategy Prediction")
 
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

                    st.markdown(

                        '<div class="result-bad">⚠️ PIT STOP LIKELY NEXT LAP</div>',

                        unsafe_allow_html=True

                    )

                    decision = "PIT"

                else:

                    st.markdown(

                        '<div class="result-good">✅ STAY OUT — NO IMMEDIATE PIT STOP</div>',

                        unsafe_allow_html=True

                    )

                    decision = "STAY OUT"
 
                m1, m2 = st.columns(2)
 
                with m1:

                    st.metric("Pit Probability", f"{pit_probability:.1f}%")
 
                with m2:

                    st.metric("Stay Out Probability", f"{stay_probability:.1f}%")
 
                st.subheader("Pit Strategy Confidence")
 
                st.progress(int(pit_probability) / 100)
 
                if pit_probability >= 70:

                    st.warning("High pit stop risk detected.")

                elif pit_probability >= 40:

                    st.info("Moderate pit stop possibility.")

                else:

                    st.success("Low pit stop probability.")
 
                st.subheader("AI Strategy Explanation")
 
                st.markdown(

                    f'<div class="explanation-box">{result["explanation"]}</div>',

                    unsafe_allow_html=True

                )
 
                st.subheader("Historical vs Predicted Strategy")
 
                compare_df = pd.DataFrame({

                    "Parameter": [

                        "Driver",

                        "Lap",

                        "Tyre Life",

                        "Compound",

                        "Track Position",

                        "Prediction"

                    ],

                    "Current Simulation": [

                        driver,

                        lap_number,

                        tyre_life,

                        compound,

                        position,

                        decision

                    ]

                })
 
                st.dataframe(compare_df, use_container_width=True)
 
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
 
st.subheader("📊 Prediction History")
 
if st.session_state.history:

    history_df = pd.DataFrame(st.session_state.history)

    st.dataframe(history_df, use_container_width=True)

else:

    st.info("No simulations executed yet.")
 