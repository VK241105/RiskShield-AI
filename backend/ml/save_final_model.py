"""
RiskShield AI
Final Production Model

The production model is trained using:
Training + Validation data = 85%

The held-out test set is NOT used for training.

The production threshold was selected separately
using validation data only.
"""

from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42

TARGET = "return_risk"


CATEGORICAL_FEATURES = [
    "payment_method",
    "product_category"
]


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "return_risk_dataset.csv"
)

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

MODEL_FILE = (
    MODEL_DIR
    / "riskshield_model.joblib"
)

THRESHOLD_FILE = (
    MODEL_DIR
    / "risk_threshold.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — FINAL PRODUCTION MODEL")
print("=" * 70)

df = pd.read_csv(
    DATA_FILE
)

X = df.drop(
    columns=[TARGET]
)

y = df[TARGET]


# ============================================================
# SPLIT
# ============================================================

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=RANDOM_STATE
)

X_validation, X_test, y_validation, y_test = (
    train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        stratify=y_temp,
        random_state=RANDOM_STATE
    )
)


# ============================================================
# COMBINE TRAIN + VALIDATION
# ============================================================

X_production = pd.concat(
    [
        X_train,
        X_validation
    ],
    axis=0
).reset_index(drop=True)


y_production = pd.concat(
    [
        y_train,
        y_validation
    ],
    axis=0
).reset_index(drop=True)


print("\nProduction training data:")

print(
    f"Samples: "
    f"{len(X_production):,}"
)

print(
    "Approximately 85% of total dataset."
)

print(
    f"\nHeld-out test samples: "
    f"{len(X_test):,}"
)

print(
    "The test set is NOT used for training."
)


# ============================================================
# NUMERICAL FEATURES
# ============================================================

NUMERICAL_FEATURES = [
    column
    for column in X.columns
    if column not in CATEGORICAL_FEATURES
]


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
# FINAL MODEL
# ============================================================

model = RandomForestClassifier(

    n_estimators=700,

    max_depth=16,

    min_samples_split=5,

    min_samples_leaf=2,

    max_features="sqrt",

    class_weight=None,

    random_state=RANDOM_STATE,

    n_jobs=-1
)


# ============================================================
# PIPELINE
# ============================================================

pipeline = Pipeline(
    steps=[

        (
            "preprocessor",
            preprocessor
        ),

        (
            "model",
            model
        )
    ]
)


# ============================================================
# TRAIN
# ============================================================

print("\nTraining production model...")

pipeline.fit(
    X_production,
    y_production
)

print(
    "Production model training completed."
)


# ============================================================
# SAVE
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    pipeline,
    MODEL_FILE
)


print("\nProduction model saved:")

print(
    MODEL_FILE
)


# ============================================================
# LOAD THRESHOLD
# ============================================================

if THRESHOLD_FILE.exists():

    threshold_data = joblib.load(
        THRESHOLD_FILE
    )

    if isinstance(
        threshold_data,
        dict
    ):

        threshold = threshold_data.get(
            "threshold",
            0.50
        )

    else:

        threshold = float(
            threshold_data
        )

else:

    threshold = 0.50

    print(
        "\nWARNING: "
        "risk_threshold.joblib not found."
    )


print(
    f"\nProduction threshold: "
    f"{threshold:.2f}"
)


# ============================================================
# VERIFY
# ============================================================

print("\nVerifying saved model...")

loaded_model = joblib.load(
    MODEL_FILE
)


sample = X_test.iloc[[0]]

sample_probability = (
    loaded_model
    .predict_proba(sample)[0][1]
)


sample_prediction = int(
    sample_probability
    >= threshold
)


print(
    f"Sample probability: "
    f"{sample_probability:.4f}"
)

print(
    f"Sample prediction: "
    f"{sample_prediction}"
)


# ============================================================
# MODEL INFORMATION
# ============================================================

print("\n" + "=" * 70)
print("PRODUCTION MODEL READY")
print("=" * 70)

print(
    "\nPipeline contains:"
)

print(
    "1. One-hot encoding"
)

print(
    "2. Numerical feature handling"
)

print(
    "3. Random Forest"
)

print(
    "4. Complete prediction pipeline"
)

print(
    "\nTraining data: 85%"
)

print(
    "Held-out test data: 15%"
)

print(
    "\nThe saved model can be loaded directly by FastAPI."
)

print("=" * 70)