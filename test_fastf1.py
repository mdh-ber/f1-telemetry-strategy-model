import fastf1
import pandas as pd

fastf1.Cache.enable_cache("cache")

session = fastf1.get_session(2023, "Monaco", "R")
session.load()

laps = session.laps

# keep only useful columns
df = laps[[
    "Driver",
    "LapNumber",
    "LapTime",
    "Stint",
    "Compound",
    "TyreLife",
    "Position"
]]

print(df.head())