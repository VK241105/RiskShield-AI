import os

import joblib
import pandas as pd


BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "../.."
    )
)


MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "riskshield_model.joblib"
)


THRESHOLD_PATH = os.path.join(
    BASE_DIR,
    "models",
    "risk_threshold.joblib"
)


print("Loading RiskShield AI model...")

model = joblib.load(
    MODEL_PATH
)

print("Model loaded successfully.")


threshold_data = joblib.load(
    THRESHOLD_PATH
)


if isinstance(
    threshold_data,
    dict
):

    THRESHOLD = float(
        threshold_data.get(
            "threshold",
            0.50
        )
    )

else:

    THRESHOLD = float(
        threshold_data
    )


print(
    f"Production threshold: "
    f"{THRESHOLD}"
)


def add_engineered_features(
    order_data: dict
):

    data = order_data.copy()

    previous_orders = max(
        data["previous_orders"],
        1
    )

    previous_returns = max(
        data["previous_returns"],
        0
    )

    previous_refunds = max(
        data["previous_refunds"],
        0
    )

    orders_last_30_days = max(
        data["orders_last_30_days"],
        0
    )

    returns_last_90_days = max(
        data["returns_last_90_days"],
        0
    )

    account_age = max(
        data["customer_account_age_days"],
        1
    )


    data["return_rate"] = min(
        (
            previous_returns
            +
            returns_last_90_days
        )
        /
        max(
            previous_orders
            +
            orders_last_30_days,
            1
        ),
        1.0
    )


    data["refund_rate"] = min(
        previous_refunds
        /
        previous_orders,
        1.0
    )


    data["recent_return_ratio"] = min(
        returns_last_90_days
        /
        max(
            orders_last_30_days + 2,
            2
        ),
        1.0
    )


    data["refund_return_ratio"] = min(
        previous_refunds
        /
        max(
            previous_returns,
            1
        ),
        1.0
    )


    data["customer_activity_rate"] = (
        previous_orders
        /
        max(
            account_age / 30,
            1
        )
    )


    data["average_order_value"] = (
        data["order_amount"]
        /
        max(
            previous_orders + 1,
            1
        )
    )


    return data


def predict_return_risk(
    order_data: dict
):

    enriched_data = (
        add_engineered_features(
            order_data
        )
    )


    input_df = pd.DataFrame(
        [enriched_data]
    )


    risk_probability = (
        model
        .predict_proba(
            input_df
        )[0][1]
    )


    prediction = int(
        risk_probability
        >= THRESHOLD
    )


    risk_score = round(
        float(risk_probability * 100),
        2
    )


    if risk_score < 30:

        risk_level = "LOW"

        recommendation = (
            "Normal processing"
        )

    elif risk_score < 60:

        risk_level = "MEDIUM"

        recommendation = (
            "Additional verification recommended"
        )

    else:

        risk_level = "HIGH"

        recommendation = (
            "Manual review recommended"
        )


    return {

        "prediction":
            "Risky"
            if prediction == 1
            else "Normal",

        "risk_probability":
            round(
                float(risk_probability),
                4
            ),

        "risk_score":
            risk_score,

        "risk_level":
            risk_level,

        "recommendation":
            recommendation
    }