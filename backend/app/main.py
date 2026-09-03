from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .schemas import OrderData, PredictionResponse
from .predictor import predict_return_risk


# ============================================================
# RISKSHIELD AI — FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RiskShield AI",
    description="AI-powered Return & Refund Risk Management API",
    version="1.0.0"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():
    return {
        "message": "RiskShield AI API is running",
        "status": "success"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# ============================================================
# PREDICTION
# ============================================================

@app.post(
    "/predict",
    response_model=PredictionResponse
)
def predict(order: OrderData):

    result = predict_return_risk(
        order.model_dump()
    )

    return result