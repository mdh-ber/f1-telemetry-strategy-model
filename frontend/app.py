import streamlit as st

import requests
 
st.set_page_config(

    page_title="PitSense AI",

    page_icon="🏎️",

    layout="wide"

)
 
st.title("🏎️ PitSense AI")

st.markdown("### F1 Pit Stop Strategy Prediction Dashboard")
 
st.sidebar.header("Race Simulation Inputs")
 
lap_number = st.sidebar.number_input("Lap Number", min_value=1, max_value=100, value=24)

tyre_life = st.sidebar.number_input("Tyre Life", min_value=1, max_value=80, value=18)

stint = st.sidebar.number_input("Stint", min_value=1, max_value=10, value=1)

position = st.sidebar.number_input("Track Position", min_value=1, max_value=20, value=3)
 
compound = st.sidebar.selectbox(

    "Tyre Compound",

    ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

)
 
driver = st.sidebar.text_input("Driver Code", value="VER")
 
st.divider()
 
col1, col2 = st.columns([1, 1])
 
with col1:

    st.subheader("Simulation Summary")

    st.write(f"**Driver:** {driver}")

    st.write(f"**Lap Number:** {lap_number}")

    st.write(f"**Tyre Life:** {tyre_life}")

    st.write(f"**Stint:** {stint}")

    st.write(f"**Track Position:** {position}")

    st.write(f"**Tyre Compound:** {compound}")
 
with col2:

    st.subheader("Prediction Result")
 
    if st.button("Predict Pit Stop", use_container_width=True):

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
 
                if result["pit_stop_next_lap"] == 1:

                    st.error("Pit Stop Likely Next Lap")

                else:

                    st.success("No Immediate Pit Stop Expected")
 
                metric1, metric2 = st.columns(2)
 
                with metric1:

                    st.metric(

                        "Pit Stop Probability",

                        round(result["probability_pit"], 3)

                    )
 
                with metric2:

                    st.metric(

                        "No Pit Probability",

                        round(result["probability_no_pit"], 3)

                    )
 
                st.subheader("Strategy Explanation")

                st.info(result["explanation"])
 
            else:

                st.error("Prediction API failed")
 
        except requests.exceptions.RequestException:

            st.error("Could not connect to backend API")
 