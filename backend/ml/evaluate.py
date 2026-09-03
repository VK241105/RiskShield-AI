from pathlib import Path

import joblib
import pandas as pd

from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
)


RANDOM_STATE = 42

# Business cost assumptions
FALSE_POSITIVE_COST = 100
FALSE_NEGATIVE_COST = 1000


def main():

    project_root = Path(__file__).resolve().parents[2]

    dataset_path = (
        project_root
        / "data"
        / "return_risk_dataset.csv"
    )

    model_path = (
        project_root
        / "models"
        / "return_risk_model.joblib"
    )

    preprocessor_path = (
        project_root
        / "models"
        / "preprocessor.joblib"
    )

    print("Loading dataset...")

    df = pd.read_csv(dataset_path)

    X = df.drop(columns=["return_risk"])
    y = df["return_risk"]

    # Load trained model
    model = joblib.load(model_path)
    preprocessor = joblib.load(
        preprocessor_path
    )

    # IMPORTANT:
    # Use the same held-out test split
    # used during training.
    from sklearn.model_selection import train_test_split

    X_train, X_temp, y_train, y_temp = train_test_split(
        X,
        y,
        test_size=0.30,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    X_validation, X_test, y_validation, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=RANDOM_STATE,
        stratify=y_temp,
    )

    X_test_processed = preprocessor.transform(
        X_test
    )

    probabilities = model.predict_proba(
        X_test_processed
    )[:, 1]

    print()
    print("=" * 65)
    print("RISKSHIELD AI — BUSINESS RISK EVALUATION")
    print("=" * 65)

    # PR-AUC
    pr_auc = average_precision_score(
        y_test,
        probabilities,
    )

    print(f"\nPR-AUC: {pr_auc:.4f}")

    # Test different thresholds
    thresholds = [
        0.30,
        0.40,
        0.50,
        0.60,
        0.70,
    ]

    print()
    print(
        "THRESHOLD ANALYSIS"
    )
    print("-" * 65)

    print(
        f"{'Threshold':<12}"
        f"{'Precision':<12}"
        f"{'Recall':<12}"
        f"{'F1':<12}"
        f"{'FP':<8}"
        f"{'FN':<8}"
        f"{'Cost':<12}"
    )

    best_threshold = None
    best_cost = float("inf")

    for threshold in thresholds:

        predictions = (
            probabilities >= threshold
        ).astype(int)

        precision = precision_score(
            y_test,
            predictions,
            zero_division=0,
        )

        recall = recall_score(
            y_test,
            predictions,
            zero_division=0,
        )

        f1 = f1_score(
            y_test,
            predictions,
            zero_division=0,
        )

        matrix = confusion_matrix(
            y_test,
            predictions,
        )

        true_negative = matrix[0][0]
        false_positive = matrix[0][1]
        false_negative = matrix[1][0]
        true_positive = matrix[1][1]

        business_cost = (
            false_positive * FALSE_POSITIVE_COST
            + false_negative * FALSE_NEGATIVE_COST
        )

        print(
            f"{threshold:<12.2f}"
            f"{precision:<12.4f}"
            f"{recall:<12.4f}"
            f"{f1:<12.4f}"
            f"{false_positive:<8}"
            f"{false_negative:<8}"
            f"₹{business_cost:<11,.0f}"
        )

        if business_cost < best_cost:
            best_cost = business_cost
            best_threshold = threshold

    print()
    print("=" * 65)
    print("BEST BUSINESS THRESHOLD")
    print("=" * 65)

    print(
        f"Threshold: {best_threshold:.2f}"
    )

    print(
        f"Estimated error cost: "
        f"₹{best_cost:,.0f}"
    )

    print()
    print("Cost assumptions:")
    print(
        f"False Positive: "
        f"₹{FALSE_POSITIVE_COST}"
    )

    print(
        f"False Negative: "
        f"₹{FALSE_NEGATIVE_COST}"
    )

    print("=" * 65)


if __name__ == "__main__":
    main()