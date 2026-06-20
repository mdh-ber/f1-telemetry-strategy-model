import pandas as pd
import os

# Load multi-race dataset
df = pd.read_csv("data/multi_race_raw.csv")

# Convert LapTime to seconds if needed
if "LapTime" in df.columns:
    df["LapTimeSeconds"] = pd.to_timedelta(df["LapTime"]).dt.total_seconds()

# Sort laps correctly
df = df.sort_values(["Driver", "Year", "Race", "LapNumber"])

# Detect actual pit stop laps
df["PitStopLap"] = (
    df.groupby(["Driver", "Year", "Race"])["Stint"]
    .diff()
    .fillna(0)
)

df["PitStopLap"] = (df["PitStopLap"] > 0).astype(int)

# Predict whether pit stop occurs on next lap
df["PitStopNextLap"] = (
    df.groupby(["Driver", "Year", "Race"])["PitStopLap"]
    .shift(-1)
    .fillna(0)
    .astype(int)
)

# Remove unrealistic lap times
df = df[
    (df["LapTimeSeconds"] > 60)
    & (df["LapTimeSeconds"] < 200)
]

# Remove rows with missing model input values
required_columns = [
    "LapNumber",
    "TyreLife",
    "Stint",
    "Position",
    "Compound",
    "Driver",
    "PitStopNextLap"
]

df = df.dropna(subset=required_columns)

os.makedirs("data/ml", exist_ok=True)

df.to_csv(
    "data/ml/multi_race_ml_dataset.csv",
    index=False
)

print("ML dataset created successfully!")
print(df.head())

print("\nDataset Shape:")
print(df.shape)

print("\nTarget Distribution:")
print(df["PitStopNextLap"].value_counts())