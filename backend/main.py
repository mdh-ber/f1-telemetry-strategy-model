from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd

app = FastAPI(title="PitSense AI Backend")

model = joblib.load("models/pitstop_prediction_model.pkl")
telemetry_df = pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")


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


@app.get("/analytics/summary")
def analytics_summary():
    return {
        "total_records": int(len(telemetry_df)),
        "total_drivers": int(telemetry_df["Driver"].nunique()),
        "total_compounds": int(telemetry_df["Compound"].nunique()),
        "average_lap_time": float(telemetry_df["LapTimeSeconds"].mean())
    }


@app.get("/analytics/drivers")
def get_drivers():
    drivers = sorted(telemetry_df["Driver"].unique().tolist())

    return {
        "drivers": drivers
    }


@app.get("/analytics/driver/{driver}")
def driver_analytics(driver: str):
    driver_code = driver.upper()

    driver_df = telemetry_df[
        telemetry_df["Driver"] == driver_code
    ]

    if driver_df.empty:
        return {
            "error": f"No telemetry found for driver {driver_code}"
        }

    return {
        "driver": driver_code,
        "average_lap_time": float(driver_df["LapTimeSeconds"].mean()),
        "fastest_lap_time": float(driver_df["LapTimeSeconds"].min()),
        "slowest_lap_time": float(driver_df["LapTimeSeconds"].max()),
        "total_laps": int(len(driver_df)),
        "stints": int(driver_df["Stint"].nunique()),
        "compounds_used": driver_df["Compound"].unique().tolist()
    }


@app.get("/analytics/compound-usage")
def compound_usage():
    compound_counts = telemetry_df["Compound"].value_counts().to_dict()

    return {
        "compound_usage": compound_counts
    }


@app.get("/analytics/pitstop-laps")
def pitstop_laps():
    pit_df = telemetry_df[
        telemetry_df["PitStopNextLap"] == 1
    ]

    records = pit_df[
        [
            "Driver",
            "LapNumber",
            "Compound",
            "TyreLife",
            "Stint",
            "Position"
        ]
    ].to_dict(orient="records")

    return {
        "pitstop_prediction_laps": records
    }