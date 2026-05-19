import fastf1
import pandas as pd
import os

# Enable cache
fastf1.Cache.enable_cache('cache')

# Load session
session = fastf1.get_session(2024, 'Monaco', 'R')
session.load()

# Get lap data
laps = session.laps

# Select important columns
selected_data = laps[[
    'Driver',
    'LapNumber',
    'LapTime',
    'Compound',
    'TyreLife',
    'Stint',
    'Position'
]]

# Create data folder if not exists
os.makedirs('data', exist_ok=True)

# Save CSV
selected_data.to_csv('data/monaco_2024_race.csv', index=False)

print("Data saved successfully!")
print(selected_data.head())