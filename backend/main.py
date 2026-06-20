from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from pathlib import Path
import joblib
import pandas as pd
import requests
import uuid
import os


def load_local_env():
    env_path = Path(".env")
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ.setdefault(key.strip(), value.strip())


load_local_env()

app = FastAPI(title="PitSense AI Backend")

model = joblib.load("models/pitstop_prediction_model.pkl")
telemetry_df = pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")

VALID_COMPOUNDS = ["SOFT", "MEDIUM", "HARD", "INTERMEDIATE", "WET"]

LANGFLOW_BASE_URL = os.getenv("LANGFLOW_BASE_URL")
LANGFLOW_FLOW_ID = os.getenv("LANGFLOW_FLOW_ID")
LANGFLOW_API_KEY = os.getenv("LANGFLOW_API_KEY")


def get_langflow_url():
    if not LANGFLOW_BASE_URL or not LANGFLOW_FLOW_ID:
        raise HTTPException(
            status_code=500,
            detail="Langflow configuration missing. Check LANGFLOW_BASE_URL and LANGFLOW_FLOW_ID in .env"
        )

    return f"{LANGFLOW_BASE_URL.rstrip('/')}/api/v1/run/{LANGFLOW_FLOW_ID}"

def build_prediction_dataframe(data):
    return pd.DataFrame([{
        "LapNumber": data.LapNumber,
        "TyreLife": data.TyreLife,
        "Stint": data.Stint,
        "Position": data.Position,
        "Compound": data.Compound,
        "Driver": data.Driver,

        "CurrentStintLap": (
            data.CurrentStintLap
            if data.CurrentStintLap is not None
            else data.TyreLife
        ),

        "PitStopsSoFar": (
            data.PitStopsSoFar
            if data.PitStopsSoFar is not None
            else max(0, int(data.Stint - 1))
        ),

        "PreviousCompound": (
            data.PreviousCompound
            if data.PreviousCompound is not None
            else data.Compound
        ),

        "PreviousStintLength": (
            data.PreviousStintLength
            if data.PreviousStintLength is not None
            else data.TyreLife
        ),

        "RaceProgress": (
            data.RaceProgress
            if data.RaceProgress is not None
            else data.LapNumber / 70.0
        ),

        "AvgLast3LapTime": (
            data.AvgLast3LapTime
            if data.AvgLast3LapTime is not None
            else 90.0
        ),

        "AvgLast5LapTime": (
            data.AvgLast5LapTime
            if data.AvgLast5LapTime is not None
            else 90.0
        ),

        "TyreDegradationRate": (
            data.TyreDegradationRate
            if data.TyreDegradationRate is not None
            else 0.0
        )
    }])

class PredictionInput(BaseModel):
    LapNumber: float
    TyreLife: float
    Stint: float
    Position: float
    Compound: str
    Driver: str

    CurrentStintLap: float | None = None
    PitStopsSoFar: float | None = None
    PreviousCompound: str | None = None
    PreviousStintLength: float | None = None
    RaceProgress: float | None = None
    AvgLast3LapTime: float | None = None
    AvgLast5LapTime: float | None = None
    TyreDegradationRate: float | None = None

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
        input_df = build_prediction_dataframe(data)
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
        input_df = build_prediction_dataframe(data)
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0].tolist()

        pit_probability = probability[1] * 100
        stay_probability = probability[0] * 100

        if prediction == 1:
            if pit_probability > 80:
                strategy_type = "critical pit window"
            elif pit_probability > 60:
                strategy_type = "high-confidence pit strategy"
            else:
                strategy_type = "moderate pit probability"

            explanation = (
                f"{data.Driver} is entering a {strategy_type}. "
                f"The telemetry indicates increasing tyre degradation on the "
                f"{data.Compound} compound after {int(data.TyreLife)} laps in the "
                f"current stint. Track position P{int(data.Position)} and lap "
                f"{int(data.LapNumber)} suggest that a pit stop could help optimize "
                f"race pace and reduce lap-time loss. The AI strategy engine identifies "
                f"the current race phase as a potential opportunity for an undercut or "
                f"tyre reset strategy."
            )

        else:
            if stay_probability > 80:
                confidence_text = "high-confidence continuation strategy"
            elif stay_probability > 60:
                confidence_text = "stable race continuation phase"
            else:
                confidence_text = "low-confidence continuation phase"

            explanation = (
                f"{data.Driver} is currently in a {confidence_text}. "
                f"The telemetry does not yet indicate severe tyre degradation or "
                f"immediate performance collapse on the {data.Compound} compound. "
                f"With tyre life at {int(data.TyreLife)} laps and track position "
                f"P{int(data.Position)}, the AI strategy engine recommends extending "
                f"the current stint to maximize tyre usage and maintain track position "
                f"efficiency."
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


@app.post("/predict-with-langflow-explanation")
def predict_with_langflow(data: PredictionInput):
    try:
        input_df = build_prediction_dataframe(data)
        prediction = model.predict(input_df)[0]
        probability = model.predict_proba(input_df)[0].tolist()

        pit_probability = round(probability[1] * 100, 1)

        fallback_explanation = (
            f"Pit probability is {pit_probability}%. "
            f"Based on lap {data.LapNumber}, tyre life {data.TyreLife}, "
            f"stint {data.Stint}, position {data.Position}, and compound {data.Compound}, "
            f"the recommended strategy is "
            f"{'PIT THIS LAP' if prediction == 1 else 'STAY OUT'}."
        )

        if not LANGFLOW_BASE_URL or not LANGFLOW_FLOW_ID:
            return {
                "pit_stop_next_lap": int(prediction),
                "probability_no_pit": probability[0],
                "probability_pit": probability[1],
                "ai_explanation": fallback_explanation
            }
        recommendation = (
            "PIT THIS LAP"
            if prediction == 1
            else "STAY OUT"
        )
        
        
        telemetry_prompt = f"""
Driver: {data.Driver}

Lap Number: {data.LapNumber}
Tyre Life: {data.TyreLife}
Current Stint: {data.Stint}
Position: {data.Position}

Current Compound: {data.Compound}
Previous Compound: {data.PreviousCompound}

Current Stint Lap: {data.CurrentStintLap}
Previous Stint Length: {data.PreviousStintLength}

Pit Stops So Far: {data.PitStopsSoFar}
Race Progress: {data.RaceProgress}

Average Last 3 Lap Time: {data.AvgLast3LapTime}
Average Last 5 Lap Time: {data.AvgLast5LapTime}

Tyre Degradation Rate: {data.TyreDegradationRate}

Predicted Pit Probability: {pit_probability}%

ML Recommendation: {recommendation}

ML Recommendation:
{"PIT THIS LAP" if pit_probability > 50 else "STAY OUT"}

Explain WHY the machine learning model produced this recommendation.
Do not generate a different recommendation.
"""

        payload = {
            "output_type": "chat",
            "input_type": "chat",
            "input_value": telemetry_prompt,
            "session_id": str(uuid.uuid4())
        }

        headers = {}
        if LANGFLOW_API_KEY:
            headers["x-api-key"] = LANGFLOW_API_KEY

        try:
            response = requests.post(
                get_langflow_url(),
                json=payload,
                headers=headers,
                timeout=120
            )

            response.raise_for_status()
            langflow_response = response.json()

            ai_explanation = None

            try:
                ai_explanation = (
                    langflow_response["outputs"][0]
                    ["outputs"][0]
                    ["results"]["message"]["text"]
                )
            except Exception:
                pass

            try:
                if not ai_explanation:
                    ai_explanation = (
                        langflow_response["outputs"][0]
                        ["outputs"][0]
                        ["artifacts"]["message"]
                    )
            except Exception:
                pass

            if not ai_explanation:
                ai_explanation = fallback_explanation

        except Exception:
            ai_explanation = fallback_explanation

        return {
            "pit_stop_next_lap": int(prediction),
            "probability_no_pit": probability[0],
            "probability_pit": probability[1],
            "ai_explanation": ai_explanation
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
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
