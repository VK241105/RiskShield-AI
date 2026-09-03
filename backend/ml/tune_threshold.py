"""
RiskShield AI
Threshold Tuning and Business Cost Evaluation

Methodology:
1. Train Random Forest using training data.
2. Use validation data to evaluate different thresholds.
3. Keep only thresholds with precision >= 50%.
4. Among those thresholds, select the one with minimum business cost.
5. Lock the selected threshold.
6. Evaluate the locked threshold on the untouched test set.

IMPORTANT:
The test set is NOT used for threshold selection.

This is a defense-only risk management system.
"""

import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
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

RANDOM_SEED = 42

# Minimum acceptable precision
MIN_PRECISION = 0.50

# Prototype business-cost assumptions
FALSE_POSITIVE_COST = 100
FALSE_NEGATIVE_COST = 1000


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "data",
    "return_risk_dataset.csv"
)

MODEL_DIR = os.path.join(
    BASE_DIR,
    "models"
)

THRESHOLD_FILE = os.path.join(
    MODEL_DIR,
    "risk_threshold.joblib"
)

THRESHOLD_CSV = os.path.join(
    MODEL_DIR,
    "threshold_analysis.csv"
)


# ============================================================
# START
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — THRESHOLD TUNING")
print("=" * 70)

print("\nLoading dataset...")

df = pd.read_csv(DATA_FILE)

print(f"Dataset shape: {df.shape}")


# ============================================================
# FEATURES AND TARGET
# ============================================================

TARGET = "return_risk"

X = df.drop(
    columns=[TARGET]
)

y = df[TARGET]


categorical_features = [
    "payment_method",
    "product_category"
]

numerical_features = [
    column
    for column in X.columns
    if column not in categorical_features
]


# ============================================================
# DATA SPLIT
# ============================================================

print("\nSplitting dataset...")

# 70% Training
# 15% Validation
# 15% Test

X_train, X_temp, y_train, y_temp = train_test_split(
    X,
    y,
    test_size=0.30,
    stratify=y,
    random_state=RANDOM_SEED
)

X_val, X_test, y_val, y_test = train_test_split(
    X_temp,
    y_temp,
    test_size=0.50,
    stratify=y_temp,
    random_state=RANDOM_SEED
)


print(f"Training samples:   {len(X_train):,}")
print(f"Validation samples: {len(X_val):,}")
print(f"Test samples:       {len(X_test):,}")


# ============================================================
# PREPROCESSING
# ============================================================

print("\nPreparing preprocessing pipeline...")

preprocessor = ColumnTransformer(
    transformers=[

        (
            "categorical",

            OneHotEncoder(
                handle_unknown="ignore",
                sparse_output=False
            ),

            categorical_features
        ),

        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# ============================================================
# RANDOM FOREST MODEL
# ============================================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(
    n_estimators=300,
    max_depth=12,
    min_samples_leaf=3,
    class_weight="balanced",
    random_state=RANDOM_SEED,
    n_jobs=-1
)


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


# Train ONLY on training data
pipeline.fit(
    X_train,
    y_train
)

print("Model training completed.")


# ============================================================
# VALIDATION PROBABILITIES
# ============================================================

print("\nCalculating validation probabilities...")

val_probabilities = pipeline.predict_proba(
    X_val
)[:, 1]


# ============================================================
# THRESHOLD ANALYSIS
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION THRESHOLD ANALYSIS")
print("=" * 70)

print(
    f"\nMinimum required precision: "
    f"{MIN_PRECISION:.0%}"
)

print(
    f"False Positive cost: ₹{FALSE_POSITIVE_COST}"
)

print(
    f"False Negative cost: ₹{FALSE_NEGATIVE_COST}"
)


# Test thresholds from 0.10 to 0.90
thresholds = np.arange(
    0.10,
    0.91,
    0.01
)


threshold_results = []


for threshold in thresholds:

    # Convert probabilities into predictions
    val_predictions = (
        val_probabilities >= threshold
    ).astype(int)


    # Classification metrics
    precision = precision_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    recall = recall_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_val,
        val_predictions,
        zero_division=0
    )


    # Confusion matrix
    tn, fp, fn, tp = confusion_matrix(
        y_val,
        val_predictions
    ).ravel()


    # Business cost
    business_cost = (
        fp * FALSE_POSITIVE_COST
        +
        fn * FALSE_NEGATIVE_COST
    )


    threshold_results.append({

        "threshold": round(
            float(threshold),
            2
        ),

        "precision": precision,

        "recall": recall,

        "f1": f1,

        "fp": int(fp),

        "fn": int(fn),

        "tp": int(tp),

        "tn": int(tn),

        "business_cost": int(
            business_cost
        ),

        "meets_precision_requirement": (
            precision >= MIN_PRECISION
        )
    })


threshold_df = pd.DataFrame(
    threshold_results
)


# ============================================================
# BEST F1 THRESHOLD
# ============================================================

best_f1_row = threshold_df.loc[
    threshold_df["f1"].idxmax()
]

best_f1_threshold = float(
    best_f1_row["threshold"]
)


print("\n" + "-" * 70)

print("BEST THRESHOLD BASED ON VALIDATION F1")

print("-" * 70)

print(
    f"Threshold     : "
    f"{best_f1_threshold:.2f}"
)

print(
    f"Precision     : "
    f"{best_f1_row['precision']:.4f}"
)

print(
    f"Recall        : "
    f"{best_f1_row['recall']:.4f}"
)

print(
    f"F1 Score      : "
    f"{best_f1_row['f1']:.4f}"
)

print(
    f"False Positives: "
    f"{int(best_f1_row['fp'])}"
)

print(
    f"False Negatives: "
    f"{int(best_f1_row['fn'])}"
)

print(
    f"Business Cost : "
    f"₹{int(best_f1_row['business_cost']):,}"
)


# ============================================================
# APPLY PRECISION CONSTRAINT
# ============================================================

valid_thresholds = threshold_df[
    threshold_df[
        "precision"
    ] >= MIN_PRECISION
].copy()


print("\n" + "-" * 70)

print("PRECISION-CONSTRAINED THRESHOLD SEARCH")

print("-" * 70)

print(
    f"Required precision: "
    f"{MIN_PRECISION:.0%}"
)

print(
    f"Valid thresholds found: "
    f"{len(valid_thresholds)}"
)


if valid_thresholds.empty:

    print(
        "\nWARNING: No threshold satisfies "
        f"the minimum precision requirement of "
        f"{MIN_PRECISION:.0%}."
    )

    print(
        "Falling back to the threshold "
        "with the best validation F1."
    )

    production_threshold = best_f1_threshold

    selected_row = best_f1_row

    selection_method = (
        "Best validation F1 because "
        "no threshold satisfied the "
        "minimum precision requirement"
    )

else:

    # Among thresholds satisfying
    # minimum precision,
    # choose the one with minimum business cost.

    selected_row = valid_thresholds.loc[
        valid_thresholds[
            "business_cost"
        ].idxmin()
    ]

    production_threshold = float(
        selected_row["threshold"]
    )

    selection_method = (
        "Minimum business cost on validation "
        f"subject to precision >= {MIN_PRECISION:.0%}"
    )


# ============================================================
# SELECTED PRODUCTION THRESHOLD
# ============================================================

print("\n" + "=" * 70)

print("SELECTED PRODUCTION THRESHOLD")

print("=" * 70)

print(
    f"\nProduction Threshold : "
    f"{production_threshold:.2f}"
)

print(
    f"Precision            : "
    f"{selected_row['precision']:.4f}"
)

print(
    f"Recall               : "
    f"{selected_row['recall']:.4f}"
)

print(
    f"F1 Score             : "
    f"{selected_row['f1']:.4f}"
)

print(
    f"False Positives      : "
    f"{int(selected_row['fp'])}"
)

print(
    f"False Negatives      : "
    f"{int(selected_row['fn'])}"
)

print(
    f"Business Cost        : "
    f"₹{int(selected_row['business_cost']):,}"
)

print(
    f"\nSelection Method:"
)

print(
    selection_method
)


# ============================================================
# VALIDATION PERFORMANCE AT LOCKED THRESHOLD
# ============================================================

val_final_predictions = (
    val_probabilities >= production_threshold
).astype(int)


val_precision = precision_score(
    y_val,
    val_final_predictions,
    zero_division=0
)

val_recall = recall_score(
    y_val,
    val_final_predictions,
    zero_division=0
)

val_f1 = f1_score(
    y_val,
    val_final_predictions,
    zero_division=0
)

val_roc_auc = roc_auc_score(
    y_val,
    val_probabilities
)

val_pr_auc = average_precision_score(
    y_val,
    val_probabilities
)


val_tn, val_fp, val_fn, val_tp = confusion_matrix(
    y_val,
    val_final_predictions
).ravel()


val_cost = (
    val_fp * FALSE_POSITIVE_COST
    +
    val_fn * FALSE_NEGATIVE_COST
)


# ============================================================
# FINAL TEST EVALUATION
# ============================================================

print("\n" + "=" * 70)

print("FINAL HELD-OUT TEST EVALUATION")

print("=" * 70)

print("\nIMPORTANT:")

print(
    "The test set was NOT used "
    "for threshold selection."
)

print(
    f"Locked production threshold: "
    f"{production_threshold:.2f}"
)


# Predict probabilities on untouched test set
test_probabilities = pipeline.predict_proba(
    X_test
)[:, 1]


# Apply locked threshold
test_predictions = (
    test_probabilities >= production_threshold
).astype(int)


# ============================================================
# TEST METRICS
# ============================================================

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


# Confusion matrix
test_tn, test_fp, test_fn, test_tp = confusion_matrix(
    y_test,
    test_predictions
).ravel()


# Business cost
test_cost = (
    test_fp * FALSE_POSITIVE_COST
    +
    test_fn * FALSE_NEGATIVE_COST
)


# ============================================================
# FINAL PERFORMANCE
# ============================================================

print("\n" + "=" * 70)

print("RISKSHIELD AI — FINAL MODEL PERFORMANCE")

print("=" * 70)

print(
    f"Threshold : "
    f"{production_threshold:.2f}"
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


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        test_predictions,
        target_names=[
            "Normal",
            "Risky"
        ],
        zero_division=0
    )
)


# ============================================================
# CONFUSION MATRIX
# ============================================================

print("Confusion Matrix:")

print(
    np.array([
        [test_tn, test_fp],
        [test_fn, test_tp]
    ])
)


# ============================================================
# BUSINESS IMPACT
# ============================================================

print("\n" + "=" * 70)

print("BUSINESS IMPACT")

print("=" * 70)

print(
    f"False Positives : "
    f"{test_fp}"
)

print(
    f"False Negatives : "
    f"{test_fn}"
)

print(
    f"True Positives  : "
    f"{test_tp}"
)

print(
    f"True Negatives  : "
    f"{test_tn}"
)

print(
    f"FP Cost/order   : "
    f"₹{FALSE_POSITIVE_COST}"
)

print(
    f"FN Cost/order   : "
    f"₹{FALSE_NEGATIVE_COST}"
)

print(
    f"Estimated Test Error Cost: "
    f"₹{test_cost:,}"
)


# ============================================================
# SAVE RESULTS
# ============================================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ============================================================
# SAVE THRESHOLD METADATA
# ============================================================

metadata = {

    "model_type": "Random Forest",

    "threshold": production_threshold,

    "threshold_selection_method": selection_method,

    "minimum_precision_requirement": MIN_PRECISION,

    "random_seed": RANDOM_SEED,

    "validation_metrics": {

        "precision": float(
            val_precision
        ),

        "recall": float(
            val_recall
        ),

        "f1": float(
            val_f1
        ),

        "roc_auc": float(
            val_roc_auc
        ),

        "pr_auc": float(
            val_pr_auc
        ),

        "true_negatives": int(
            val_tn
        ),

        "false_positives": int(
            val_fp
        ),

        "false_negatives": int(
            val_fn
        ),

        "true_positives": int(
            val_tp
        ),

        "business_cost": int(
            val_cost
        )
    },

    "test_metrics": {

        "precision": float(
            test_precision
        ),

        "recall": float(
            test_recall
        ),

        "f1": float(
            test_f1
        ),

        "roc_auc": float(
            test_roc_auc
        ),

        "pr_auc": float(
            test_pr_auc
        ),

        "true_negatives": int(
            test_tn
        ),

        "false_positives": int(
            test_fp
        ),

        "false_negatives": int(
            test_fn
        ),

        "true_positives": int(
            test_tp
        ),

        "business_cost": int(
            test_cost
        )
    },

    "business_cost_assumptions": {

        "false_positive_cost": (
            FALSE_POSITIVE_COST
        ),

        "false_negative_cost": (
            FALSE_NEGATIVE_COST
        )
    },

    "data_type": (
        "Synthetic prototype data"
    ),

    "test_set_used_for_threshold_selection": False
}


joblib.dump(
    metadata,
    THRESHOLD_FILE
)


# ============================================================
# SAVE THRESHOLD ANALYSIS CSV
# ============================================================

threshold_df.to_csv(
    THRESHOLD_CSV,
    index=False
)


# ============================================================
# COMPLETION
# ============================================================

print("\n" + "=" * 70)

print("THRESHOLD TUNING COMPLETED")

print("=" * 70)

print(
    f"\nProduction threshold: "
    f"{production_threshold:.2f}"
)

print(
    f"\nThreshold metadata saved to:"
)

print(
    THRESHOLD_FILE
)

print(
    f"\nThreshold analysis saved to:"
)

print(
    THRESHOLD_CSV
)

print(
    "\nThe test set was evaluated "
    "only after the threshold was locked."
)

print(
    "\nThe threshold was selected using "
    "validation data only."
)

print("=" * 70)