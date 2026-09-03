"""
RiskShield AI
Threshold Tuning and Business Cost Evaluation

Methodology:

1. Train model on training data.
2. Generate validation probabilities.
3. Search thresholds on validation data.
4. Require minimum precision.
5. Select threshold with minimum business cost.
6. Lock threshold.
7. Evaluate locked threshold on test set.
8. Save threshold metadata.

The test set is NEVER used to select the threshold.
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
    confusion_matrix
)


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_STATE = 42

MIN_PRECISION = 0.60

FALSE_POSITIVE_COST = 100

FALSE_NEGATIVE_COST = 1000


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

THRESHOLD_CSV = (
    PROJECT_ROOT
    / "models"
    / "threshold_analysis.csv"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — THRESHOLD TUNING")
print("=" * 70)

df = pd.read_csv(
    DATA_FILE
)

X = df.drop(
    columns=["return_risk"]
)

y = df["return_risk"]


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
# LOAD MODEL
# ============================================================

model = joblib.load(
    MODEL_FILE
)


# ============================================================
# VALIDATION PROBABILITIES
# ============================================================

validation_probabilities = (
    model.predict_proba(
        X_validation
    )[:, 1]
)


# ============================================================
# THRESHOLD SEARCH
# ============================================================

thresholds = np.arange(
    0.20,
    0.81,
    0.01
)


results = []


for threshold in thresholds:

    predictions = (
        validation_probabilities
        >= threshold
    ).astype(int)


    accuracy = accuracy_score(
        y_validation,
        predictions
    )

    precision = precision_score(
        y_validation,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_validation,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_validation,
        predictions,
        zero_division=0
    )


    tn, fp, fn, tp = (
        confusion_matrix(
            y_validation,
            predictions
        ).ravel()
    )


    business_cost = (
        fp * FALSE_POSITIVE_COST
        +
        fn * FALSE_NEGATIVE_COST
    )


    results.append({

        "threshold":
            round(float(threshold), 2),

        "accuracy":
            accuracy,

        "precision":
            precision,

        "recall":
            recall,

        "f1":
            f1,

        "tn":
            int(tn),

        "fp":
            int(fp),

        "fn":
            int(fn),

        "tp":
            int(tp),

        "business_cost":
            int(business_cost),

        "meets_precision":
            precision >= MIN_PRECISION
    })


threshold_df = pd.DataFrame(
    results
)


# ============================================================
# VALID THRESHOLDS
# ============================================================

valid = threshold_df[
    threshold_df["meets_precision"]
].copy()


print("\n" + "=" * 70)
print("VALIDATION THRESHOLD ANALYSIS")
print("=" * 70)

print(
    f"\nMinimum precision: "
    f"{MIN_PRECISION:.0%}"
)

print(
    f"Valid thresholds: "
    f"{len(valid)}"
)


# ============================================================
# SELECT THRESHOLD
# ============================================================

if len(valid) == 0:

    print(
        "\nNo threshold satisfied "
        "the precision requirement."
    )

    print(
        "Selecting threshold with "
        "best validation F1."
    )

    selected = threshold_df.loc[
        threshold_df["f1"].idxmax()
    ]

    selection_method = (
        "Best validation F1"
    )

else:

    # Primary objective:
    # minimum business cost

    # Tie-break:
    # higher F1

    # Final tie-break:
    # higher precision

    valid = valid.sort_values(
        by=[
            "business_cost",
            "f1",
            "precision"
        ],
        ascending=[
            True,
            False,
            False
        ]
    )

    selected = valid.iloc[0]

    selection_method = (
        "Minimum validation business cost "
        f"with precision >= {MIN_PRECISION:.0%}"
    )


production_threshold = float(
    selected["threshold"]
)


# ============================================================
# LOCKED THRESHOLD
# ============================================================

print("\n" + "=" * 70)
print("LOCKED PRODUCTION THRESHOLD")
print("=" * 70)

print(
    f"\nThreshold : "
    f"{production_threshold:.2f}"
)

print(
    f"Precision : "
    f"{selected['precision']:.4f}"
)

print(
    f"Recall    : "
    f"{selected['recall']:.4f}"
)

print(
    f"F1        : "
    f"{selected['f1']:.4f}"
)

print(
    f"Accuracy  : "
    f"{selected['accuracy']:.4f}"
)

print(
    f"Business Cost: "
    f"₹{int(selected['business_cost']):,}"
)

print(
    f"\nSelection method:\n"
    f"{selection_method}"
)


# ============================================================
# FINAL TEST EVALUATION
# ============================================================

test_probabilities = (
    model.predict_proba(
        X_test
    )[:, 1]
)

test_predictions = (
    test_probabilities
    >= production_threshold
).astype(int)


test_accuracy = accuracy_score(
    y_test,
    test_predictions
)

test_precision = precision_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_recall = recall_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_f1 = f1_score(
    y_test,
    test_predictions,
    zero_division=0
)

test_roc_auc = roc_auc_score(
    y_test,
    test_probabilities
)

test_pr_auc = average_precision_score(
    y_test,
    test_probabilities
)


test_tn, test_fp, test_fn, test_tp = (
    confusion_matrix(
        y_test,
        test_predictions
    ).ravel()
)


test_cost = (
    test_fp * FALSE_POSITIVE_COST
    +
    test_fn * FALSE_NEGATIVE_COST
)


# ============================================================
# TEST RESULTS
# ============================================================

print("\n" + "=" * 70)
print("FINAL HELD-OUT TEST")
print("=" * 70)

print(
    f"\nLocked threshold: "
    f"{production_threshold:.2f}"
)

print(
    f"Accuracy  : "
    f"{test_accuracy:.4f}"
)

print(
    f"Precision : "
    f"{test_precision:.4f}"
)

print(
    f"Recall    : "
    f"{test_recall:.4f}"
)

print(
    f"F1 Score  : "
    f"{test_f1:.4f}"
)

print(
    f"ROC-AUC   : "
    f"{test_roc_auc:.4f}"
)

print(
    f"PR-AUC    : "
    f"{test_pr_auc:.4f}"
)


print("\nConfusion Matrix:")

print(
    [
        [test_tn, test_fp],
        [test_fn, test_tp]
    ]
)


print(
    f"\nEstimated test error cost: "
    f"₹{test_cost:,}"
)


# ============================================================
# SAVE METADATA
# ============================================================

MODEL_DIR = PROJECT_ROOT / "models"

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


metadata = {

    "model_type":
        "Best validation model",

    "threshold":
        production_threshold,

    "threshold_selection_method":
        selection_method,

    "minimum_precision_requirement":
        MIN_PRECISION,

    "random_seed":
        RANDOM_STATE,

    "validation_metrics":
        selected.to_dict(),

    "test_metrics": {

        "accuracy":
            float(test_accuracy),

        "precision":
            float(test_precision),

        "recall":
            float(test_recall),

        "f1":
            float(test_f1),

        "roc_auc":
            float(test_roc_auc),

        "pr_auc":
            float(test_pr_auc),

        "tn":
            int(test_tn),

        "fp":
            int(test_fp),

        "fn":
            int(test_fn),

        "tp":
            int(test_tp),

        "business_cost":
            int(test_cost)
    },

    "business_cost_assumptions": {

        "false_positive_cost":
            FALSE_POSITIVE_COST,

        "false_negative_cost":
            FALSE_NEGATIVE_COST
    },

    "data_type":
        "Synthetic prototype data",

    "test_set_used_for_threshold_selection":
        False
}


joblib.dump(
    metadata,
    THRESHOLD_FILE
)


threshold_df.to_csv(
    THRESHOLD_CSV,
    index=False
)


print("\nThreshold metadata saved:")
print(THRESHOLD_FILE)

print("\nThreshold analysis saved:")
print(THRESHOLD_CSV)

print("\nThreshold tuning completed.")
print("=" * 70)