import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

DATA_FILE = os.path.join(
    BASE_DIR, "data", "return_risk_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR, "models"
)

MODEL_FILE = os.path.join(
    MODEL_DIR, "riskshield_model.joblib"
)

THRESHOLD_FILE = os.path.join(
    MODEL_DIR, "risk_threshold.joblib"
)


# ============================================================
# SETTINGS
# ============================================================

TARGET = "return_risk"

RANDOM_STATE = 42

CATEGORICAL_FEATURES = [
    "payment_method",
    "product_category"
]


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — SAVING FINAL MODEL")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset shape: {df.shape}")


# ============================================================
# PREPARE FEATURES
# ============================================================

X = df.drop(columns=[TARGET])
y = df[TARGET]

NUMERICAL_FEATURES = [
    col for col in X.columns
    if col not in CATEGORICAL_FEATURES
]

print("\nFeatures:")
print(f"Categorical: {CATEGORICAL_FEATURES}")
print(f"Numerical  : {NUMERICAL_FEATURES}")


# ============================================================
# SAME DATA SPLIT USED DURING FINAL EVALUATION
# ============================================================

# First split:
# 70% Train
# 30% Temporary

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=RANDOM_STATE
)

# Second split:
# 15% Validation
# 15% Test

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=RANDOM_STATE
)

print("\nData split:")
print(f"Training   : {len(X_train)}")
print(f"Validation : {len(X_val)}")
print(f"Test       : {len(X_test)}")


# ============================================================
# PREPROCESSOR
# ============================================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),
            CATEGORICAL_FEATURES
        ),
        (
            "numerical",
            "passthrough",
            NUMERICAL_FEATURES
        )
    ]
)


# ============================================================
# FINAL RANDOM FOREST MODEL
# ============================================================

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=RANDOM_STATE,
    n_jobs=-1
)


# ============================================================
# COMPLETE PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ============================================================
# TRAIN MODEL
# ============================================================

print("\nTraining final model...")

pipeline.fit(X_train, y_train)

print("Model training completed.")


# ============================================================
# CREATE MODEL DIRECTORY
# ============================================================

os.makedirs(MODEL_DIR, exist_ok=True)


# ============================================================
# SAVE COMPLETE PIPELINE
# ============================================================

joblib.dump(
    pipeline,
    MODEL_FILE
)

print("\nFinal model saved successfully:")
print(MODEL_FILE)


# ============================================================
# LOAD THRESHOLD
# ============================================================

if os.path.exists(THRESHOLD_FILE):

    threshold_data = joblib.load(THRESHOLD_FILE)

    print("\nProduction threshold information:")

    if isinstance(threshold_data, dict):
        threshold = threshold_data.get(
            "threshold",
            threshold_data.get("production_threshold", None)
        )

        print(f"Production threshold: {threshold}")

    else:
        print(f"Production threshold: {threshold_data}")

else:
    print("\nWARNING: risk_threshold.joblib was not found.")


# ============================================================
# VERIFY SAVED MODEL
# ============================================================

print("\nVerifying saved model...")

loaded_pipeline = joblib.load(MODEL_FILE)

sample = X_test.iloc[[0]]

prediction = loaded_pipeline.predict(sample)[0]

probability = loaded_pipeline.predict_proba(sample)[0][1]

print(f"Sample prediction : {prediction}")
print(f"Sample risk probability: {probability:.4f}")


# ============================================================
# FINAL INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("FINAL MODEL READY")
print("=" * 70)

print(f"Model file:")
print(MODEL_FILE)

print("\nThe saved pipeline contains:")
print("1. Categorical preprocessing")
print("2. Numerical preprocessing")
print("3. Random Forest model")
print("4. Complete prediction pipeline")

print("\nThe model can now be loaded directly by FastAPI.")

print("=" * 70)