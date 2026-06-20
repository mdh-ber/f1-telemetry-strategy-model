import pandas as pd
import os

# Load multi-race dataset
df = pd.read_csv("data/multi_race_2024_raw.csv")

# Convert LapTime to seconds
if "LapTime" in df.columns:
    df["LapTimeSeconds"] = pd.to_timedelta(
        df["LapTime"],
        errors="coerce"
    ).dt.total_seconds()

# Sort laps correctly
df = df.sort_values(["Year", "Race", "Driver", "LapNumber"])

group_cols = ["Year", "Race", "Driver"]

# Detect actual pit stop lap
df["PitStopLap"] = (
    df.groupby(group_cols)["Stint"]
    .diff()
    .fillna(0)
)

df["PitStopLap"] = (df["PitStopLap"] > 0).astype(int)

# Predict whether pit stop occurs on next lap
df["PitStopNextLap"] = (
    df.groupby(group_cols)["PitStopLap"]
    .shift(-1)
    .fillna(0)
    .astype(int)
)

# New race-context features
df["CurrentStintLap"] = (
    df.groupby(["Year", "Race", "Driver", "Stint"])
    .cumcount() + 1
)

df["PitStopsSoFar"] = (
    df.groupby(group_cols)["PitStopLap"]
    .cumsum()
    .shift(1)
    .fillna(0)
    .astype(int)
)

df["PreviousCompound"] = (
    df.groupby(group_cols)["Compound"]
    .shift(1)
    .fillna("UNKNOWN")
)

df["PreviousStintLength"] = (
    df.groupby(["Year", "Race", "Driver", "Stint"])["LapNumber"]
    .transform("count")
)

df["RaceProgress"] = (
    df["LapNumber"] /
    df.groupby(["Year", "Race"])["LapNumber"].transform("max")
)

df["AvgLast3LapTime"] = (
    df.groupby(group_cols)["LapTimeSeconds"]
    .transform(lambda x: x.rolling(3, min_periods=1).mean())
)

df["AvgLast5LapTime"] = (
    df.groupby(group_cols)["LapTimeSeconds"]
    .transform(lambda x: x.rolling(5, min_periods=1).mean())
)

df["TyreDegradationRate"] = (
    df.groupby(group_cols)["LapTimeSeconds"]
    .diff()
    .fillna(0)
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
    "CurrentStintLap",
    "PitStopsSoFar",
    "PreviousCompound",
    "PreviousStintLength",
    "RaceProgress",
    "AvgLast3LapTime",
    "AvgLast5LapTime",
    "TyreDegradationRate",
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

print("\nNew Feature Preview:")
print(
    df[
        [
            "Driver",
            "LapNumber",
            "Stint",
            "Compound",
            "CurrentStintLap",
            "PitStopsSoFar",
            "PreviousCompound",
            "PreviousStintLength",
            "RaceProgress",
            "AvgLast3LapTime",
            "AvgLast5LapTime",
            "TyreDegradationRate",
            "PitStopNextLap"
        ]
    ].head(15)
)