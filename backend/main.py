from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
import joblib
import pandas as pd

app = FastAPI(title="PitSense AI Backend")

model = joblib.load("models/pitstop_prediction_model.pkl")
telemetry_df = pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")

VALID_COMPOUNDS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]


class PredictionInput(BaseModel):
    LapNumber: float
    TyreLife: float
    Stint: float
    Position: float
    Compound: str
    Driver: str

    @validator("LapNumber")
    def validate_lap(cls, value):
        if value < 1 or value > 100:
            raise ValueError("LapNumber must be between 1 and 100")
        return value

    @validator("TyreLife")
    def validate_tyre_life(cls, value):
        if value < 0 or value > 80:
            raise ValueError("TyreLife must be between 0 and 80")
        return value

    @validator("Stint")
    def validate_stint(cls, value):
        if value < 1 or value > 10:
            raise ValueError("Stint must be between 1 and 10")
        return value

    @validator("Position")
    def validate_position(cls, value):
        if value < 1 or value > 20:
            raise ValueError("Position must be between 1 and 20")
        return value

    @validator("Compound")
    def validate_compound(cls, value):
        compound = value.upper()
        if compound not in VALID_COMPOUNDS:
            raise ValueError(f"Compound must be one of {VALID_COMPOUNDS}")
        return compound

    @validator("Driver")
    def validate_driver(cls, value):
        driver = value.upper().strip()
        if len(driver) < 2:
            raise ValueError("Driver code is too short")
        return driver


@app.get("/")
def home():
    return {"message": "PitSense AI backend is running"}


@app.post("/predict")
def predict_pitstop(data: PredictionInput):
    try:
        input_df = pd.DataFrame([data.dict()])
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0].tolist()

        return {
            "pit_stop_next_lap": int(prediction),
            "probability_no_pit": probability[0],
            "probability_pit": probability[1]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.post("/predict-with-explanation")
def predict_with_explanation(data: PredictionInput):
    try:
        input_df = pd.DataFrame([data.dict()])
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0].tolist()

        if prediction == 1:
            explanation = (
                f"Pit stop is likely on the next lap for {data.Driver}. "
                f"The model detected a stronger pit pattern using lap {data.LapNumber}, "
                f"tyre age {data.TyreLife}, stint {data.Stint}, "
                f"track position {data.Position}, and tyre compound {data.Compound}."
            )
        else:
            explanation = (
                f"Pit stop is not likely on the next lap for {data.Driver}. "
                f"The telemetry currently suggests a continuation strategy rather "
                f"than an immediate pit window."
            )

        return {
            "pit_stop_next_lap": int(prediction),
            "probability_no_pit": probability[0],
            "probability_pit": probability[1],
            "explanation": explanation
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction explanation failed: {str(e)}"
        )


@app.get("/analytics/summary")
def analytics_summary():
    try:
        return {
            "total_records": int(len(telemetry_df)),
            "total_drivers": int(telemetry_df["Driver"].nunique()),
            "total_compounds": int(telemetry_df["Compound"].nunique()),
            "average_lap_time": float(telemetry_df["LapTimeSeconds"].mean())
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Analytics summary failed: {str(e)}"
        )


@app.get("/analytics/drivers")
def get_drivers():
    try:
        drivers = sorted(telemetry_df["Driver"].unique().tolist())
        return {"drivers": drivers}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Driver retrieval failed: {str(e)}"
        )


@app.get("/analytics/driver/{driver}")
def driver_analytics(driver: str):
    try:
        driver_code = driver.upper()

        driver_df = telemetry_df[
            telemetry_df["Driver"] == driver_code
        ]

        if driver_df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No telemetry found for driver {driver_code}"
            )

        return {
            "driver": driver_code,
            "average_lap_time": float(driver_df["LapTimeSeconds"].mean()),
            "fastest_lap_time": float(driver_df["LapTimeSeconds"].min()),
            "slowest_lap_time": float(driver_df["LapTimeSeconds"].max()),
            "total_laps": int(len(driver_df)),
            "stints": int(driver_df["Stint"].nunique()),
            "compounds_used": driver_df["Compound"].unique().tolist()
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Driver analytics failed: {str(e)}"
        )


@app.get("/analytics/compound-usage")
def compound_usage():
    try:
        compound_counts = telemetry_df["Compound"].value_counts().to_dict()
        return {"compound_usage": compound_counts}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Compound analytics failed: {str(e)}"
        )


@app.get("/analytics/pitstop-laps")
def pitstop_laps():
    try:
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

        return {"pitstop_prediction_laps": records}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Pit stop analytics failed: {str(e)}"
        )