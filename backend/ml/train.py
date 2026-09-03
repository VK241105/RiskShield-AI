from pathlib import Path

import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder


RANDOM_STATE = 42


def main():

    # Find project folder
    project_root = Path(__file__).resolve().parents[2]

    # Dataset location
    dataset_path = project_root / "data" / "return_risk_dataset.csv"

    # Model folder
    model_directory = project_root / "models"
    model_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    print(f"Dataset shape: {df.shape}")

    # Target
    target_column = "return_risk"

    X = df.drop(columns=[target_column])
    y = df[target_column]

    # Categorical columns
    categorical_features = [
        "payment_method",
        "product_category",
    ]

    # Numerical columns
    numerical_features = [
        column
        for column in X.columns
        if column not in categorical_features
    ]

    # Preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(
                    handle_unknown="ignore",
                    sparse_output=False,
                ),
                categorical_features,
            ),
            (
                "numerical",
                "passthrough",
                numerical_features,
            ),
        ]
    )

    # --------------------------------
    # Split data
    # --------------------------------

    print("\nSplitting dataset...")

    # 70% training, 30% temporary
    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    # Temporary data -> 15% validation + 15% test
    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    print(f"Training samples:   {len(X_train):,}")
    print(f"Validation samples: {len(X_validation):,}")
    print(f"Test samples:       {len(X_test):,}")

    # --------------------------------
    # Preprocessing
    # --------------------------------

    print("\nProcessing data...")

    X_train_processed = preprocessor.fit_transform(
        X_train
    )

    X_validation_processed = preprocessor.transform(
        X_validation
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    # --------------------------------
    # Train Random Forest
    # --------------------------------

    print("\nTraining Random Forest AI model...")

    model = RandomForestClassifier(
        n_estimators=300,
        max_depth=12,
        min_samples_leaf=3,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    model.fit(
        X_train_processed,
        y_train,
    )

    # --------------------------------
    # Validation
    # --------------------------------

    print("\nEvaluating validation set...")

    validation_probabilities = model.predict_proba(
        X_validation_processed
    )[:, 1]

    validation_predictions = (
        validation_probabilities >= 0.50
    ).astype(int)

    validation_f1 = f1_score(
        y_validation,
        validation_predictions,
        zero_division=0,
    )

    print(
        f"Validation F1 Score: {validation_f1:.4f}"
    )

    # --------------------------------
    # Held-out TEST SET
    # --------------------------------

    print("\nEvaluating HELD-OUT TEST SET...")

    test_probabilities = model.predict_proba(
        X_test_processed
    )[:, 1]

    test_predictions = (
        test_probabilities >= 0.50
    ).astype(int)

    precision = precision_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    recall = recall_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    f1 = f1_score(
        y_test,
        test_predictions,
        zero_division=0,
    )

    roc_auc = roc_auc_score(
        y_test,
        test_probabilities,
    )

    # --------------------------------
    # Results
    # --------------------------------

    print("\n" + "=" * 60)
    print("RISKSHIELD AI — MODEL PERFORMANCE")
    print("=" * 60)

    print(f"Precision : {precision:.4f}")
    print(f"Recall    : {recall:.4f}")
    print(f"F1 Score  : {f1:.4f}")
    print(f"ROC-AUC   : {roc_auc:.4f}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            test_predictions,
            target_names=[
                "Normal",
                "Risky",
            ],
            zero_division=0,
        )
    )

    print("Confusion Matrix:")

    matrix = confusion_matrix(
        y_test,
        test_predictions,
    )

    print(matrix)

    # --------------------------------
    # Save model
    # --------------------------------

    model_path = (
        model_directory
        / "return_risk_model.joblib"
    )

    preprocessor_path = (
        model_directory
        / "preprocessor.joblib"
    )

    joblib.dump(
        model,
        model_path,
    )

    joblib.dump(
        preprocessor,
        preprocessor_path,
    )

    print("\n" + "=" * 60)
    print("MODEL SAVED SUCCESSFULLY")
    print("=" * 60)

    print(f"Model: {model_path}")
    print(f"Preprocessor: {preprocessor_path}")

    print("=" * 60)


if __name__ == "__main__":
    main()
    