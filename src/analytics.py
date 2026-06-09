import pandas as pd

df = pd.read_csv("data/processed/monaco_2024_processed.csv")

print("\nAverage lap time by driver:")
print(df.groupby("Driver")["LapTimeSeconds"].mean().sort_values())

print("\nAverage lap time by tyre compound:")
print(df.groupby("Compound")["LapTimeSeconds"].mean().sort_values())

print("\nNumber of stints by driver:")
print(df.groupby("Driver")["Stint"].nunique().sort_values(ascending=False))

print("\nPit stop indicators:")
df["PitStopLap"] = df.groupby("Driver")["Stint"].diff().fillna(0)
print(df[df["PitStopLap"] > 0][["Driver", "LapNumber", "Compound", "Stint"]])