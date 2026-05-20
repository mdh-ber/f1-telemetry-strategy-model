import streamlit as st

import requests
 
st.title("PitSense AI")

st.subheader("F1 Pit Stop Prediction Dashboard")
 
lap_number = st.number_input("Lap Number", min_value=1, max_value=100, value=24)

tyre_life = st.number_input("Tyre Life", min_value=1, max_value=80, value=18)

stint = st.number_input("Stint", min_value=1, max_value=10, value=1)

position = st.number_input("Track Position", min_value=1, max_value=20, value=3)
 
compound = st.selectbox(

    "Tyre Compound",

    ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

)
 
driver = st.text_input("Driver Code", value="VER")
 
if st.button("Predict Pit Stop"):
 
    payload = {

        "LapNumber": lap_number,

        "TyreLife": tyre_life,

        "Stint": stint,

        "Position": position,

        "Compound": compound,

        "Driver": driver

    }
 
    response = requests.post(

        "http://backend:8000/predict-with-explanation",

        json=payload

    )
 
    if response.status_code == 200:
 
        result = response.json()
 
        st.success("Prediction Complete")
 
        st.metric(

            "Pit Stop Next Lap",

            result["pit_stop_next_lap"]

        )
 
        st.metric(

            "Probability of Pit Stop",

            round(result["probability_pit"], 3)

        )
 
        st.metric(

            "Probability of No Pit Stop",

            round(result["probability_no_pit"], 3)

        )
 
        st.subheader("Strategy Explanation")

        st.write(result["explanation"])
 
    else:

        st.error("Prediction API failed")
 