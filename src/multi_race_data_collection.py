import fastf1
import pandas as pd
import os
from datetime import datetime

fastf1.Cache.enable_cache("cache")

START_YEAR = 2022
END_YEAR = datetime.now().year

all_data = []

for year in range(START_YEAR, END_YEAR + 1):
    print(f"\n==============================")
    print(f"Loading race schedule for {year}")
    print(f"==============================")

    try:
        schedule = fastf1.get_event_schedule(year)
        races = schedule[schedule["EventFormat"] != "testing"]
    except Exception as e:
        print(f"Failed to load schedule for {year}: {e}")
        continue

    for _, event in races.iterrows():
        race_name = event["EventName"]

        try:
            print(f"Loading {year} {race_name} Race...")

            session = fastf1.get_session(year, race_name, "R")
            session.load()

            laps = session.laps.copy()

            selected = laps[
                [
                    "Driver",
                    "LapNumber",
                    "LapTime",
                    "Compound",
                    "TyreLife",
                    "Stint",
                    "Position",
                ]
            ].copy()

            selected["Year"] = year
            selected["Race"] = race_name

            all_data.append(selected)

            print(f"Added {year} {race_name}: {len(selected)} rows")

        except Exception as e:
            print(f"Skipped {year} {race_name}: {e}")

if not all_data:
    raise RuntimeError("No race data was collected.")

combined_df = pd.concat(all_data, ignore_index=True)

os.makedirs("data", exist_ok=True)
combined_df.to_csv("data/multi_race_raw.csv", index=False)

print("\nMulti-race data saved successfully!")
print("Saved to: data/multi_race_raw.csv")
print("Total rows:", len(combined_df))
print("Years:", sorted(combined_df["Year"].unique()))
print("Races:", combined_df["Race"].nunique())
print(combined_df.head())