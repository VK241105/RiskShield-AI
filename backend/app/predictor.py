import os
import joblib
import pandas as pd


# ------------------------------------------------------------
# PATHS
# ------------------------------------------------------------

BASE_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
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


# ------------------------------------------------------------
# LOAD MODEL
# ------------------------------------------------------------

print("Loading RiskShield AI model...")

model = joblib.load(MODEL_PATH)

print("Model loaded successfully.")


# ------------------------------------------------------------
# LOAD PRODUCTION THRESHOLD
# ------------------------------------------------------------

threshold_data = joblib.load(THRESHOLD_PATH)

if isinstance(threshold_data, dict):
    THRESHOLD = threshold_data.get(
        "threshold",
        threshold_data.get("production_threshold", 0.43)
    )
else:
    THRESHOLD = float(threshold_data)

print(f"Production threshold: {THRESHOLD}")


# ------------------------------------------------------------
# PREDICTION FUNCTION
# ------------------------------------------------------------

def predict_return_risk(order_data: dict):

    # Convert incoming data into DataFrame
    input_df = pd.DataFrame([order_data])

    # Get probability of risky return
    risk_probability = model.predict_proba(input_df)[0][1]

    # Apply locked production threshold
    prediction = int(risk_probability >= THRESHOLD)

    # Convert probability to score 0-100
    risk_score = round(risk_probability * 100, 2)

    # Risk level
    if risk_score < 30:
        risk_level = "LOW"

    elif risk_score < 60:
        risk_level = "MEDIUM"

    else:
        risk_level = "HIGH"

    # Recommendation
    if risk_level == "LOW":
        recommendation = "Normal processing"

    elif risk_level == "MEDIUM":
        recommendation = "Additional verification recommended"

    else:
        recommendation = "Manual review recommended"

    return {
        "prediction": "Risky" if prediction == 1 else "Normal",
        "risk_probability": round(float(risk_probability), 4),
        "risk_score": risk_score,
        "risk_level": risk_level,
        "recommendation": recommendation
    }