"""
RiskShield AI
Model Evaluation

IMPORTANT:
This script ONLY evaluates the locked model/threshold.

The test set is never used for model or threshold selection.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix,
    classification_report
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42


# ============================================================
# PATHS
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_FILE = (
    PROJECT_ROOT
    / "data"
    / "return_risk_dataset.csv"
)

MODEL_FILE = (
    PROJECT_ROOT
    / "models"
    / "riskshield_model.joblib"
)

THRESHOLD_FILE = (
    PROJECT_ROOT
    / "models"
    / "risk_threshold.joblib"
)


# ============================================================
# LOAD
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — FINAL EVALUATION")
print("=" * 70)

df = pd.read_csv(DATA_FILE)

X = df.drop(
    columns=["return_risk"]
)

y = df["return_risk"]


model = joblib.load(
    MODEL_FILE
)

threshold_data = joblib.load(
    THRESHOLD_FILE
)


if isinstance(
    threshold_data,
    dict
):

    threshold = float(
        threshold_data["threshold"]
    )

else:

    threshold = float(
        threshold_data
    )


# ============================================================
# SAME SPLIT
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
# TEST PREDICTIONS
# ============================================================

probabilities = (
    model.predict_proba(
        X_test
    )[:, 1]
)

predictions = (
    probabilities >= threshold
).astype(int)


# ============================================================
# METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    predictions
)

precision = precision_score(
    y_test,
    predictions,
    zero_division=0
)

recall = recall_score(
    y_test,
    predictions,
    zero_division=0
)

f1 = f1_score(
    y_test,
    predictions,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    probabilities
)

pr_auc = average_precision_score(
    y_test,
    probabilities
)


tn, fp, fn, tp = confusion_matrix(
    y_test,
    predictions
).ravel()


# ============================================================
# BUSINESS COST
# ============================================================

FALSE_POSITIVE_COST = 100
FALSE_NEGATIVE_COST = 1000

business_cost = (
    fp * FALSE_POSITIVE_COST
    +
    fn * FALSE_NEGATIVE_COST
)


# ============================================================
# OUTPUT
# ============================================================

print("\n" + "=" * 70)
print("FINAL HELD-OUT TEST RESULTS")
print("=" * 70)

print(
    f"\nThreshold : {threshold:.2f}"
)

print(
    f"Accuracy  : {accuracy:.4f}"
)

print(
    f"Precision : {precision:.4f}"
)

print(
    f"Recall    : {recall:.4f}"
)

print(
    f"F1 Score  : {f1:.4f}"
)

print(
    f"ROC-AUC   : {roc_auc:.4f}"
)

print(
    f"PR-AUC    : {pr_auc:.4f}"
)


print("\nConfusion Matrix:")

print(
    np.array([
        [tn, fp],
        [fn, tp]
    ])
)


print("\nClassification Report:")

print(
    classification_report(
        y_test,
        predictions,
        target_names=[
            "Normal",
            "Risky"
        ],
        zero_division=0
    )
)


print("\nBusiness Impact:")

print(
    f"False Positives : {fp}"
)

print(
    f"False Negatives : {fn}"
)

print(
    f"True Positives  : {tp}"
)

print(
    f"True Negatives  : {tn}"
)

print(
    f"Estimated error cost: ₹{business_cost:,}"
)


print("\nIMPORTANT:")

print(
    "The test set was used only for final evaluation."
)

print(
    "It was not used to select the model or threshold."
)

print("\n" + "=" * 70)