import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score

df = pd.read_csv("data/ml/monaco_2024_ml_dataset.csv")

features = [
    "LapNumber",
    "TyreLife",
    "Stint",
    "Position",
    "Compound",
    "Driver"
]

target = "PitStopNextLap"

X = df[features]
y = df[target]

categorical_features = ["Compound", "Driver"]
numeric_features = ["LapNumber", "TyreLife", "Stint", "Position"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ("num", "passthrough", numeric_features)
    ]
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=100,
            random_state=42,
            class_weight="balanced"
        ))
    ]
)

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

print("Model training completed!")
print("\nAccuracy:", accuracy_score(y_test, y_pred))
print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))
print("\nClassification Report:")
print(classification_report(y_test, y_pred, zero_division=0))

os.makedirs("models", exist_ok=True)
joblib.dump(model, "models/pitstop_prediction_model.pkl")

print("\nModel saved to models/pitstop_prediction_model.pkl")