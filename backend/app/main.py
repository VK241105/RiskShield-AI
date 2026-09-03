from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
import os

from .database import (
    delete_all_assessments,
    delete_assessment,
    initialize_database,
    list_assessments,
    record_assessment,
    update_review
)
from .schemas import OrderData, PredictionResponse, ReviewUpdate
from .predictor import THRESHOLD, model, predict_return_risk


# ============================================================
# RISKSHIELD AI — FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="RiskShield AI",
    description="AI-powered Return & Refund Risk Management API",
    version="1.0.0"
)

initialize_database()

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "RISKSHIELD_ALLOWED_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173"
    ).split(",")
    if origin.strip()
]

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
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
        "status": "healthy",
        "model_loaded": model is not None,
        "threshold_loaded": THRESHOLD is not None
    }


@app.get("/assessments")
def assessments():
    return {"assessments": list_assessments()}


@app.patch("/assessments/{assessment_id}/review")
def review_assessment(assessment_id: int, review: ReviewUpdate):
    assessment = update_review(
        assessment_id,
        review.review_status,
        review.reviewer_note
    )
    if assessment is None:
        raise HTTPException(status_code=404, detail="Assessment not found")
    return assessment


@app.delete("/assessments/{assessment_id}", status_code=204)
def remove_assessment(assessment_id: int):
    if not delete_assessment(assessment_id):
        raise HTTPException(status_code=404, detail="Assessment not found")


@app.delete("/assessments", status_code=204)
def remove_all_assessments():
    delete_all_assessments()


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

    assessment_id = record_assessment(order.model_dump(), result)
    result["assessment_id"] = assessment_id

    return result