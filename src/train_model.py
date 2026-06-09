import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = "data/ml/monaco_2024_ml_dataset.csv"
MODEL_PATH = "models/pitstop_prediction_model.pkl"

df = pd.read_csv(DATA_PATH)

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

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

models = {
    "Logistic Regression": LogisticRegression(
        max_iter=1000,
        class_weight="balanced"
    ),
    "Decision Tree": DecisionTreeClassifier(
        random_state=42,
        class_weight="balanced"
    ),
    "Random Forest": RandomForestClassifier(
        n_estimators=100,
        random_state=42,
        class_weight="balanced"
    ),
    "Gradient Boosting": GradientBoostingClassifier(
        random_state=42
    )
}

results = []

print("\n==============================")
print("COMPARATIVE MODEL EVALUATION")
print("==============================")

for model_name, classifier in models.items():
    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ]
    )

    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    results.append({
        "Model": model_name,
        "Accuracy": accuracy,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1
    })

    print(f"\nModel: {model_name}")
    print(f"Accuracy : {accuracy:.4f}")
    print(f"Precision: {precision:.4f}")
    print(f"Recall   : {recall:.4f}")
    print(f"F1 Score : {f1:.4f}")

results_df = pd.DataFrame(results)
print("\n==============================")
print("MODEL COMPARISON SUMMARY")
print("==============================")
print(results_df.sort_values(by="F1 Score", ascending=False))

print("\n==============================")
print("HYPERPARAMETER OPTIMIZATION")
print("==============================")

rf_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            random_state=42,
            class_weight="balanced"
        ))
    ]
)

param_grid = {
    "classifier__n_estimators": [50, 100, 200],
    "classifier__max_depth": [5, 10, None],
    "classifier__min_samples_split": [2, 5],
    "classifier__min_samples_leaf": [1, 2]
}

grid_search = GridSearchCV(
    estimator=rf_pipeline,
    param_grid=param_grid,
    cv=3,
    scoring="f1",
    n_jobs=-1
)

grid_search.fit(X_train, y_train)

best_model = grid_search.best_estimator_

print("Best Parameters:")
print(grid_search.best_params_)

print("Best Cross Validation F1 Score:")
print(grid_search.best_score_)

print("\n==============================")
print("FINAL MODEL BENCHMARK")
print("==============================")

final_predictions = best_model.predict(X_test)

print("\nAccuracy:", accuracy_score(y_test, final_predictions))
print("Precision:", precision_score(y_test, final_predictions, zero_division=0))
print("Recall:", recall_score(y_test, final_predictions, zero_division=0))
print("F1 Score:", f1_score(y_test, final_predictions, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, final_predictions))

print("\nClassification Report:")
print(classification_report(y_test, final_predictions, zero_division=0))

print("\n==============================")
print("FEATURE IMPORTANCE ANALYSIS")
print("==============================")

classifier = best_model.named_steps["classifier"]
preprocessor_fitted = best_model.named_steps["preprocessor"]

try:
    encoded_cat_features = list(
        preprocessor_fitted
        .named_transformers_["cat"]
        .get_feature_names_out(categorical_features)
    )

    all_feature_names = encoded_cat_features + numeric_features

    if hasattr(classifier, "feature_importances_"):
        importances = classifier.feature_importances_

        feature_importance_df = pd.DataFrame({
            "Feature": all_feature_names,
            "Importance": importances
        }).sort_values(by="Importance", ascending=False)

        print(feature_importance_df.head(15))
    else:
        print("Selected classifier does not support feature_importances_.")

except Exception as e:
    print("Feature importance could not be generated.")
    print(str(e))

os.makedirs("models", exist_ok=True)
joblib.dump(best_model, MODEL_PATH)

print("\n==============================")
print("MODEL SAVED")
print("==============================")
print(f"Final optimized model saved to {MODEL_PATH}")