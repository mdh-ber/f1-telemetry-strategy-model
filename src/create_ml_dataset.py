import pandas as pd
import os

df = pd.read_csv("data/processed/monaco_2024_processed.csv")

df = df.sort_values(["Driver", "LapNumber"])

# Detect actual pit stop lap
df["PitStopLap"] = df.groupby("Driver")["Stint"].diff().fillna(0)
df["PitStopLap"] = (df["PitStopLap"] > 0).astype(int)

# Predict whether pit stop happens on next lap
df["PitStopNextLap"] = df.groupby("Driver")["PitStopLap"].shift(-1).fillna(0).astype(int)

# Remove rows where lap time is unrealistic, like safety car / red flag effects
df = df[(df["LapTimeSeconds"] > 60) & (df["LapTimeSeconds"] < 200)]

os.makedirs("data/ml", exist_ok=True)

df.to_csv("data/ml/monaco_2024_ml_dataset.csv", index=False)

print("ML dataset created successfully!")
print(df.head())
print("\nTarget distribution:")
print(df["PitStopNextLap"].value_counts())