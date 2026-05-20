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
 