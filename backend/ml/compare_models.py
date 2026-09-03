"""
RiskShield AI
Model Comparison

IMPORTANT:
- Validation set is used for model selection.
- Test set is reported separately.
- Test results must NOT be used to choose a model.
"""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    HistGradientBoostingClassifier
)

from xgboost import XGBClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score
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

MODEL_DIR = (
    PROJECT_ROOT
    / "models"
)

COMPARISON_FILE = (
    MODEL_DIR
    / "model_comparison.csv"
)

BEST_MODEL_FILE = (
    MODEL_DIR
    / "best_return_risk_model.joblib"
)

METADATA_FILE = (
    MODEL_DIR
    / "model_metadata.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

print("=" * 75)
print("RISKSHIELD AI — MODEL COMPARISON")
print("=" * 75)

df = pd.read_csv(DATA_FILE)

TARGET = "return_risk"

X = df.drop(
    columns=[TARGET]
)

y = df[TARGET]


CATEGORICAL_FEATURES = [
    "payment_method",
    "product_category"
]

NUMERICAL_FEATURES = [
    column
    for column in X.columns
    if column not in CATEGORICAL_FEATURES
]


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
# PREPROCESSOR
# ============================================================

def create_preprocessor():

    return ColumnTransformer(
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
# MODELS
# ============================================================

negative_count = (
    y_train == 0
).sum()

positive_count = (
    y_train == 1
).sum()

scale_pos_weight = (
    negative_count
    /
    positive_count
)


models = {

    "Logistic Regression":
        LogisticRegression(
            max_iter=3000,
            C=1.0,
            random_state=RANDOM_STATE
        ),

    "Random Forest":
        RandomForestClassifier(
            n_estimators=500,
            max_depth=14,
            min_samples_split=5,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight=None,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),

    "Extra Trees":
        ExtraTreesClassifier(
            n_estimators=500,
            max_depth=16,
            min_samples_split=4,
            min_samples_leaf=2,
            max_features="sqrt",
            class_weight=None,
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),

    "XGBoost":
        XGBClassifier(
            n_estimators=500,
            max_depth=5,
            learning_rate=0.04,
            subsample=0.90,
            colsample_bytree=0.90,
            min_child_weight=2,
            gamma=0.05,
            reg_alpha=0.05,
            reg_lambda=1.5,
            objective="binary:logistic",
            eval_metric="logloss",
            scale_pos_weight=1.0,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
}


# ============================================================
# TRAIN / COMPARE
# ============================================================

results = []

trained_pipelines = {}


for model_name, model in models.items():

    print(
        f"\nTraining: {model_name}"
    )

    pipeline = Pipeline(
        steps=[

            (
                "preprocessor",
                create_preprocessor()
            ),

            (
                "model",
                model
            )
        ]
    )

    pipeline.fit(
        X_train,
        y_train
    )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    val_probabilities = (
        pipeline.predict_proba(
            X_validation
        )[:, 1]
    )

    val_predictions = (
        val_probabilities >= 0.50
    ).astype(int)

    val_accuracy = accuracy_score(
        y_validation,
        val_predictions
    )

    val_precision = precision_score(
        y_validation,
        val_predictions,
        zero_division=0
    )

    val_recall = recall_score(
        y_validation,
        val_predictions,
        zero_division=0
    )

    val_f1 = f1_score(
        y_validation,
        val_predictions,
        zero_division=0
    )

    val_roc_auc = roc_auc_score(
        y_validation,
        val_probabilities
    )

    val_pr_auc = average_precision_score(
        y_validation,
        val_probabilities
    )

    # --------------------------------------------------------
    # TEST
    # --------------------------------------------------------

    test_probabilities = (
        pipeline.predict_proba(
            X_test
        )[:, 1]
    )

    test_predictions = (
        test_probabilities >= 0.50
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

    results.append({

        "model": model_name,

        "validation_accuracy":
            val_accuracy,

        "validation_precision":
            val_precision,

        "validation_recall":
            val_recall,

        "validation_f1":
            val_f1,

        "validation_roc_auc":
            val_roc_auc,

        "validation_pr_auc":
            val_pr_auc,

        "test_accuracy":
            test_accuracy,

        "test_precision":
            test_precision,

        "test_recall":
            test_recall,

        "test_f1":
            test_f1,

        "test_roc_auc":
            test_roc_auc,

        "test_pr_auc":
            test_pr_auc
    })

    trained_pipelines[model_name] = pipeline


# ============================================================
# RESULTS
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    by="validation_f1",
    ascending=False
).reset_index(drop=True)


print("\n" + "=" * 75)
print("MODEL COMPARISON")
print("=" * 75)

print(
    results_df.to_string(
        index=False,
        float_format=lambda x: f"{x:.4f}"
    )
)


# ============================================================
# SELECT BEST MODEL
# ============================================================

best_model_name = (
    results_df.iloc[0]["model"]
)

best_pipeline = (
    trained_pipelines[best_model_name]
)


print("\n" + "=" * 75)
print("BEST MODEL")
print("=" * 75)

print(
    f"Selected model: {best_model_name}"
)

print(
    "Selection metric: Validation F1"
)


# ============================================================
# SAVE
# ============================================================

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)

results_df.to_csv(
    COMPARISON_FILE,
    index=False
)

joblib.dump(
    best_pipeline,
    BEST_MODEL_FILE
)

metadata = {

    "best_model":
        best_model_name,

    "selection_metric":
        "validation_f1",

    "random_state":
        RANDOM_STATE,

    "test_used_for_model_selection":
        False,

    "data_type":
        "Synthetic prototype data"
}

joblib.dump(
    metadata,
    METADATA_FILE
)


print("\nSaved:")

print(COMPARISON_FILE)
print(BEST_MODEL_FILE)
print(METADATA_FILE)

print("=" * 75)