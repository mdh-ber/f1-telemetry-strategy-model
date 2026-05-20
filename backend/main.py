from fastapi import FastAPI

from pydantic import BaseModel

import joblib

import pandas as pd
 
app = FastAPI(title="PitSense AI Backend")
 
model = joblib.load("models/pitstop_prediction_model.pkl")
 
 
class PredictionInput(BaseModel):

    LapNumber: float

    TyreLife: float

    Stint: float

    Position: float

    Compound: str

    Driver: str
 
 
@app.get("/")

def home():

    return {"message": "PitSense AI backend is running"}
 
 
@app.post("/predict")

def predict_pitstop(data: PredictionInput):

    input_df = pd.DataFrame([data.dict()])
 
    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0].tolist()
 
    return {

        "pit_stop_next_lap": int(prediction),

        "probability_no_pit": probability[0],

        "probability_pit": probability[1]

    }
@app.post("/predict-with-explanation")

def predict_with_explanation(data: PredictionInput):

    input_df = pd.DataFrame([data.dict()])

    prediction = model.predict(input_df)[0]

    probability = model.predict_proba(input_df)[0].tolist()

    if prediction == 1:

        explanation = (

            f"Pit stop is likely on the next lap for {data.Driver}. "

            f"The model detected a higher pit-stop pattern based on lap {data.LapNumber}, "

            f"tyre age of {data.TyreLife} laps, stint {data.Stint}, position {data.Position}, "

            f"and current compound {data.Compound}."

        )

    else:

        explanation = (

            f"Pit stop is not likely on the next lap for {data.Driver}. "

            f"The model sees the current tyre age, stint, track position, and compound as closer "

            f"to a continuation strategy rather than an immediate pit stop."

        )

    return {

        "pit_stop_next_lap": int(prediction),

        "probability_no_pit": probability[0],

        "probability_pit": probability[1],

        "explanation": explanation

    }
 