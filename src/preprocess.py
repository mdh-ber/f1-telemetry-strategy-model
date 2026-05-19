import pandas as pd
import os

df = pd.read_csv("data/monaco_2024_race.csv")

df = df.dropna(subset=["LapTime"])

df["LapTimeSeconds"] = pd.to_timedelta(df["LapTime"]).dt.total_seconds()

df = df.drop(columns=["LapTime"])

os.makedirs("data/processed", exist_ok=True)

df.to_csv("data/processed/monaco_2024_processed.csv", index=False)

print("Preprocessed data saved successfully!")
print(df.head())
print(df.info())