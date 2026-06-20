import os
import joblib
import pandas as pd
import shap

from sklearn.model_selection import train_test_split, GridSearchCV, RandomizedSearchCV
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier


from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

DATA_PATH = "data/ml/multi_race_ml_dataset.csv"
MODEL_PATH = "models/pitstop_prediction_model.pkl"

df = pd.read_csv(DATA_PATH)

print("\n==============================")
print("DATASET INFORMATION")
print("==============================")
print("Dataset path:", DATA_PATH)
print("Dataset shape:", df.shape)
print("\nTarget distribution:")
print(df["PitStopNextLap"].value_counts())
print("\nTarget distribution (%):")
print(df["PitStopNextLap"].value_counts(normalize=True) * 100)

features = [
    "LapNumber",
    "TyreLife",
    "Stint",
    "Position",
    "Compound",
    "Driver",
    "CurrentStintLap",
    "PitStopsSoFar",
    "PreviousCompound",
    "PreviousStintLength",
    "RaceProgress",
    "AvgLast3LapTime",
    "AvgLast5LapTime",
    "TyreDegradationRate"
]

target = "PitStopNextLap"

X = df[features]
y = df[target]

categorical_features = [
    "Compound",
    "Driver",
    "PreviousCompound"
]

numeric_features = [
    "LapNumber",
    "TyreLife",
    "Stint",
    "Position",
    "CurrentStintLap",
    "PitStopsSoFar",
    "PreviousStintLength",
    "RaceProgress",
    "AvgLast3LapTime",
    "AvgLast5LapTime",
    "TyreDegradationRate"
]

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

print("\nTrain target distribution:")
print(y_train.value_counts())

print("\nTest target distribution:")
print(y_test.value_counts())

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
    ),
    "XGBoost": XGBClassifier(
        n_estimators=100,
        max_depth=6,
        learning_rate=0.1,
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
    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

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
print("RANDOMIZED SEARCH OPTIMIZATION")
print("==============================")

random_search_pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            random_state=42,
            class_weight="balanced"
        ))
    ]
)

random_param_grid = {
    "classifier__n_estimators": [50, 100, 200, 300],
    "classifier__max_depth": [5, 10, 20, None],
    "classifier__min_samples_split": [2, 5, 10],
    "classifier__min_samples_leaf": [1, 2, 4]
}

random_search = RandomizedSearchCV(
    estimator=random_search_pipeline,
    param_distributions=random_param_grid,
    n_iter=10,
    cv=3,
    scoring="f1",
    random_state=42,
    n_jobs=-1
)

random_search.fit(X_train, y_train)

print("Randomized Search Best Parameters:")
print(random_search.best_params_)

print("Randomized Search Best Cross Validation F1 Score:")
print(random_search.best_score_)


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

print("\nPrediction distribution:")
print(pd.Series(final_predictions).value_counts())

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

        print(feature_importance_df.head(20))
    else:
        print("Selected classifier does not support feature_importances_.")

except Exception as e:
    print("Feature importance could not be generated.")
    print(str(e))

os.makedirs("models", exist_ok=True)
joblib.dump(best_model, MODEL_PATH)


print("\n==============================")
print("SHAP EXPLAINABILITY ANALYSIS")
print("==============================")

try:
    X_test_transformed = preprocessor_fitted.transform(X_test)

    if hasattr(X_test_transformed, "toarray"):
        X_test_transformed = X_test_transformed.toarray()

    explainer = shap.TreeExplainer(classifier)
    shap_values = explainer.shap_values(X_test_transformed)

    if isinstance(shap_values, list):
        shap_values_for_class = shap_values[1]
    elif len(shap_values.shape) == 3:
        shap_values_for_class = shap_values[:, :, 1]
    else:
        shap_values_for_class = shap_values

    mean_shap_values = abs(shap_values_for_class).mean(axis=0)

    shap_importance_df = pd.DataFrame({
        "Feature": all_feature_names,
        "Mean_SHAP_Importance": mean_shap_values
    }).sort_values(by="Mean_SHAP_Importance", ascending=False)

    print("Top SHAP Features:")
    print(shap_importance_df.head(15))

except Exception as e:
    print("SHAP analysis could not be generated.")
    print(str(e))

    

print("\n==============================")
print("MODEL SAVED")
print("==============================")
print(f"Final optimized model saved to {MODEL_PATH}")