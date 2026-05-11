import streamlit as st
import requests

st.title("PitSense AI")
st.subheader("F1 Pit Stop Strategy Prediction")

driver = st.selectbox(
    "Select Driver",
    ["Max Verstappen", "Lewis Hamilton", "Charles Leclerc"]
)

lap = st.slider("Lap Number", 1, 70, 20)

if st.button("Predict Pit Stop"):

    response = requests.get("http://backend:8000/predict")

    if response.status_code == 200:
        data = response.json()

        st.success("Prediction Generated")

        st.write("Pit Stop Probability:")
        st.write(data["pit_stop_probability"])

        st.write("Recommended Pit Window:")
        st.write(data["recommended_pit_window"])