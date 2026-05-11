from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def home():
    return {"message": "PitSense AI Backend Running"}

@app.get("/predict")
def predict():
    return {
        "pit_stop_probability": "78%",
        "recommended_pit_window": "Lap 18 - 20"
    }