import os
import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    average_precision_score,
    confusion_matrix
)

from xgboost import XGBClassifier


# ============================================================
# RISKSHIELD AI
# MODEL COMPARISON
#
# Models:
# 1. Logistic Regression
# 2. Random Forest
# 3. XGBoost
#
# IMPORTANT:
# The held-out test set is used ONLY for final comparison.
# Model selection should primarily use validation performance.
# ============================================================


RANDOM_STATE = 42


def evaluate_model(model_name, model, X_train, y_train, X_val, y_val, X_test, y_test):

    print()
    print("=" * 65)
    print(f"TRAINING: {model_name}")
    print("=" * 65)

    # --------------------------------------------------------
    # Train
    # --------------------------------------------------------

    model.fit(X_train, y_train)

    # --------------------------------------------------------
    # Validation predictions
    # --------------------------------------------------------

    val_predictions = model.predict(X_val)
    val_probabilities = model.predict_proba(X_val)[:, 1]

    val_precision = precision_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    val_recall = recall_score(
        y_val,
        val_predictions,
        zero_division=0
    )

    val_f1 = f1_score(
        y_val,
        val_predictions,
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

    # --------------------------------------------------------
    # Test predictions
    # --------------------------------------------------------

    test_predictions = model.predict(X_test)
    test_probabilities = model.predict_proba(X_test)[:, 1]

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

    test_cm = confusion_matrix(
        y_test,
        test_predictions
    )

    # --------------------------------------------------------
    # Display validation results
    # --------------------------------------------------------

    print()
    print("VALIDATION RESULTS")
    print("-" * 65)

    print(f"Precision : {val_precision:.4f}")
    print(f"Recall    : {val_recall:.4f}")
    print(f"F1 Score  : {val_f1:.4f}")
    print(f"ROC-AUC   : {val_roc_auc:.4f}")
    print(f"PR-AUC    : {val_pr_auc:.4f}")

    # --------------------------------------------------------
    # Display test results
    # --------------------------------------------------------

    print()
    print("HELD-OUT TEST RESULTS")
    print("-" * 65)

    print(f"Precision : {test_precision:.4f}")
    print(f"Recall    : {test_recall:.4f}")
    print(f"F1 Score  : {test_f1:.4f}")
    print(f"ROC-AUC   : {test_roc_auc:.4f}")
    print(f"PR-AUC    : {test_pr_auc:.4f}")

    print()
    print("CONFUSION MATRIX")
    print("-" * 65)

    print(test_cm)

    # --------------------------------------------------------
    # Return results
    # --------------------------------------------------------

    return {
        "model": model_name,

        "val_precision": val_precision,
        "val_recall": val_recall,
        "val_f1": val_f1,
        "val_roc_auc": val_roc_auc,
        "val_pr_auc": val_pr_auc,

        "test_precision": test_precision,
        "test_recall": test_recall,
        "test_f1": test_f1,
        "test_roc_auc": test_roc_auc,
        "test_pr_auc": test_pr_auc,

        "confusion_matrix": test_cm,

        "trained_model": model
    }


def main():

    print("=" * 65)
    print("RISKSHIELD AI — MODEL COMPARISON")
    print("=" * 65)

    # --------------------------------------------------------
    # 1. Paths
    # --------------------------------------------------------

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            ".."
        )
    )

    dataset_path = os.path.join(
        project_root,
        "data",
        "return_risk_dataset.csv"
    )

    models_directory = os.path.join(
        project_root,
        "models"
    )

    os.makedirs(
        models_directory,
        exist_ok=True
    )

    # --------------------------------------------------------
    # 2. Load dataset
    # --------------------------------------------------------

    print()
    print("Loading dataset...")

    if not os.path.exists(dataset_path):

        print()
        print("ERROR: Dataset not found.")
        print(f"Expected location: {dataset_path}")

        return

    df = pd.read_csv(dataset_path)

    print(f"Dataset shape: {df.shape}")

    # --------------------------------------------------------
    # 3. Separate features and target
    # --------------------------------------------------------

    target_column = "return_risk"

    X = df.drop(
        columns=[target_column]
    )

    y = df[target_column]

    print()
    print("CLASS DISTRIBUTION")
    print("-" * 65)

    print(
        y.value_counts()
        .sort_index()
        .rename(
            index={
                0: "Normal",
                1: "Risky"
            }
        )
    )

    # --------------------------------------------------------
    # 4. Identify feature types
    # --------------------------------------------------------

    categorical_features = [
        "payment_method",
        "product_category"
    ]

    numerical_features = [
        column
        for column in X.columns
        if column not in categorical_features
    ]

    # --------------------------------------------------------
    # 5. Split data
    #
    # 70% Training
    # 15% Validation
    # 15% Held-out Test
    # --------------------------------------------------------

    print()
    print("Splitting dataset...")

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y
    )

    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp
    )

    print(f"Training samples:   {len(X_train):,}")
    print(f"Validation samples: {len(X_val):,}")
    print(f"Test samples:       {len(X_test):,}")

    # --------------------------------------------------------
    # 6. Preprocessor
    # --------------------------------------------------------

    print()
    print("Preparing preprocessing pipeline...")

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "num",
                "passthrough",
                numerical_features
            ),
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False
                ),
                categorical_features
            )
        ]
    )

    # --------------------------------------------------------
    # 7. Calculate class imbalance
    # --------------------------------------------------------

    negative_count = np.sum(y_train == 0)
    positive_count = np.sum(y_train == 1)

    scale_pos_weight = (
        negative_count / positive_count
        if positive_count > 0
        else 1.0
    )

    print()
    print("Class imbalance:")
    print(f"Normal training samples: {negative_count:,}")
    print(f"Risky training samples:  {positive_count:,}")
    print(f"XGBoost scale_pos_weight: {scale_pos_weight:.3f}")

    # --------------------------------------------------------
    # 8. Define models
    # --------------------------------------------------------

    models = {

        "Logistic Regression": LogisticRegression(
            max_iter=2000,
            class_weight="balanced",
            random_state=RANDOM_STATE
        ),

        "Random Forest": RandomForestClassifier(
            n_estimators=300,
            max_depth=12,
            min_samples_leaf=3,
            class_weight="balanced",
            random_state=RANDOM_STATE,
            n_jobs=-1
        ),

        "XGBoost": XGBClassifier(
            n_estimators=300,
            max_depth=5,
            learning_rate=0.05,
            subsample=0.85,
            colsample_bytree=0.85,
            min_child_weight=3,
            gamma=0.1,
            reg_alpha=0.1,
            reg_lambda=1.0,
            objective="binary:logistic",
            eval_metric="logloss",
            scale_pos_weight=scale_pos_weight,
            random_state=RANDOM_STATE,
            n_jobs=-1
        )
    }

    # --------------------------------------------------------
    # 9. Train and evaluate models
    # --------------------------------------------------------

    results = []

    trained_models = {}

    for model_name, classifier in models.items():

        pipeline = Pipeline(
            steps=[
                (
                    "preprocessor",
                    preprocessor
                ),
                (
                    "classifier",
                    classifier
                )
            ]
        )

        result = evaluate_model(
            model_name,
            pipeline,
            X_train,
            y_train,
            X_val,
            y_val,
            X_test,
            y_test
        )

        trained_models[model_name] = pipeline

        results.append(
            result
        )

    # --------------------------------------------------------
    # 10. Create comparison table
    # --------------------------------------------------------

    print()
    print()
    print("=" * 90)
    print("RISKSHIELD AI — FINAL MODEL COMPARISON")
    print("=" * 90)

    comparison_data = []

    for result in results:

        comparison_data.append({

            "Model":
                result["model"],

            "Val Precision":
                round(
                    result["val_precision"],
                    4
                ),

            "Val Recall":
                round(
                    result["val_recall"],
                    4
                ),

            "Val F1":
                round(
                    result["val_f1"],
                    4
                ),

            "Val ROC-AUC":
                round(
                    result["val_roc_auc"],
                    4
                ),

            "Test Precision":
                round(
                    result["test_precision"],
                    4
                ),

            "Test Recall":
                round(
                    result["test_recall"],
                    4
                ),

            "Test F1":
                round(
                    result["test_f1"],
                    4
                ),

            "Test ROC-AUC":
                round(
                    result["test_roc_auc"],
                    4
                ),

            "Test PR-AUC":
                round(
                    result["test_pr_auc"],
                    4
                )
        })

    comparison_df = pd.DataFrame(
        comparison_data
    )

    print(
        comparison_df.to_string(
            index=False
        )
    )

    # --------------------------------------------------------
    # 11. Select best model using VALIDATION F1
    #
    # IMPORTANT:
    # We do NOT select the final model using test F1.
    # The test set remains a final unbiased evaluation.
    # --------------------------------------------------------

    best_result = max(
        results,
        key=lambda result:
        result["val_f1"]
    )

    best_model_name = best_result["model"]

    best_model = trained_models[
        best_model_name
    ]

    print()
    print("=" * 65)
    print("BEST MODEL BASED ON VALIDATION F1")
    print("=" * 65)

    print(
        f"Selected model: {best_model_name}"
    )

    print(
        f"Validation F1: "
        f"{best_result['val_f1']:.4f}"
    )

    print(
        f"Validation Precision: "
        f"{best_result['val_precision']:.4f}"
    )

    print(
        f"Validation Recall: "
        f"{best_result['val_recall']:.4f}"
    )

    print(
        f"Validation ROC-AUC: "
        f"{best_result['val_roc_auc']:.4f}"
    )

    # --------------------------------------------------------
    # 12. Display selected model's held-out test metrics
    # --------------------------------------------------------

    print()
    print("SELECTED MODEL — HELD-OUT TEST PERFORMANCE")
    print("-" * 65)

    print(
        f"Test Precision : "
        f"{best_result['test_precision']:.4f}"
    )

    print(
        f"Test Recall    : "
        f"{best_result['test_recall']:.4f}"
    )

    print(
        f"Test F1 Score  : "
        f"{best_result['test_f1']:.4f}"
    )

    print(
        f"Test ROC-AUC   : "
        f"{best_result['test_roc_auc']:.4f}"
    )

    print(
        f"Test PR-AUC    : "
        f"{best_result['test_pr_auc']:.4f}"
    )

    print()
    print("Test Confusion Matrix:")
    print(
        best_result["confusion_matrix"]
    )

    # --------------------------------------------------------
    # 13. Save comparison results
    # --------------------------------------------------------

    comparison_path = os.path.join(
        models_directory,
        "model_comparison.csv"
    )

    comparison_df.to_csv(
        comparison_path,
        index=False
    )

    # --------------------------------------------------------
    # 14. Save best model
    # --------------------------------------------------------

    best_model_path = os.path.join(
        models_directory,
        "best_return_risk_model.joblib"
    )

    joblib.dump(
        best_model,
        best_model_path
    )

    # --------------------------------------------------------
    # 15. Save model metadata
    # --------------------------------------------------------

    metadata = {
        "selected_model": best_model_name,
        "selection_metric": "validation_f1",

        "validation_precision":
            best_result["val_precision"],

        "validation_recall":
            best_result["val_recall"],

        "validation_f1":
            best_result["val_f1"],

        "validation_roc_auc":
            best_result["val_roc_auc"],

        "test_precision":
            best_result["test_precision"],

        "test_recall":
            best_result["test_recall"],

        "test_f1":
            best_result["test_f1"],

        "test_roc_auc":
            best_result["test_roc_auc"],

        "test_pr_auc":
            best_result["test_pr_auc"],

        "random_state":
            RANDOM_STATE,

        "dataset_type":
            "Synthetic prototype dataset"
    }

    metadata_path = os.path.join(
        models_directory,
        "model_metadata.joblib"
    )

    joblib.dump(
        metadata,
        metadata_path
    )

    # --------------------------------------------------------
    # 16. Final message
    # --------------------------------------------------------

    print()
    print("=" * 65)
    print("MODEL COMPARISON COMPLETED")
    print("=" * 65)

    print(
        f"Comparison saved to:"
    )

    print(comparison_path)

    print()
    print(
        f"Best model saved to:"
    )

    print(best_model_path)

    print()
    print(
        f"Metadata saved to:"
    )

    print(metadata_path)

    print("=" * 65)


if __name__ == "__main__":
    main()
    