F1 Pit Stop Strategy

Project Overview

This project applies Machine Learning techniques to analyze and predict pit stop strategies in Formula 1 racing using real telemetry and race data.

The goal is not to “perfectly optimize race strategy,” but to model and predict pit stop decision patterns based on historical race behavior, tyre usage, and lap performance trends.

---

Objectives

- Collect and process Formula 1 telemetry data
- Analyze race strategies across drivers and teams
- Identify patterns in pit stop decisions
- Build a machine learning model to predict:
  - Whether a pit stop is likely on a given lap
  - Or the probable pit stop window
- Deploy the model using a simple API and containerized environment

---

Dataset

We use the Python library:

- **FastF1 API** (Formula 1 telemetry and session data)

Data includes:
- Lap times
- Tyre compounds
- Stint information
- Track conditions
- Driver performance metrics

## 🏗️ System Architecture
