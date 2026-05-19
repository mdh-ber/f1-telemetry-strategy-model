import fastf1
import pandas as pd
import os

fastf1.Cache.enable_cache("cache")

races = [
    (2024, "Bahrain"),
    (2024, "Saudi Arabia"),
    (2024, "Australia"),
    (2024, "Japan"),
    (2024, "China"),
    (2024, "Miami"),
    (2024, "Emilia Romagna"),
    (2024, "Monaco"),
    (2024, "Canada"),
    (2024, "Spain"),
]

all_data = []

for year, race in races:
    try:
        print(f"Loading {year} {race} Race...")
        session = fastf1.get_session(year, race, "R")
        session.load()

        laps = session.laps.copy()

        selected = laps[[
            "Driver",
            "LapNumber",
            "LapTime",
            "Compound",
            "TyreLife",
            "Stint",
            "Position"
        ]].copy()

        selected["Year"] = year
        selected["Race"] = race

        all_data.append(selected)

        print(f"Added {year} {race}")

    except Exception as e:
        print(f"Failed {year} {race}: {e}")

combined_df = pd.concat(all_data, ignore_index=True)

os.makedirs("data", exist_ok=True)

combined_df.to_csv("data/multi_race_2024_raw.csv", index=False)

print("Multi-race data saved successfully!")
print(combined_df.head())
print("Total rows:", len(combined_df))