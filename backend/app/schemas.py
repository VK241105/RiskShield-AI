from pydantic import BaseModel, Field


class OrderData(BaseModel):

    customer_age: float = Field(
        ...,
        ge=18,
        le=100
    )

    order_amount: float = Field(
        ...,
        ge=0
    )

    previous_orders: int = Field(
        ...,
        ge=0
    )

    previous_returns: int = Field(
        ...,
        ge=0
    )

    previous_refunds: int = Field(
        ...,
        ge=0
    )

    delivery_days: float = Field(
        ...,
        ge=0
    )

    discount_percentage: float = Field(
        ...,
        ge=0,
        le=100
    )

    customer_account_age_days: int = Field(
        ...,
        ge=0
    )

    orders_last_30_days: int = Field(
        ...,
        ge=0
    )

    returns_last_90_days: int = Field(
        ...,
        ge=0
    )

    payment_method: str = Field(
        ...,
        min_length=1
    )

    product_category: str = Field(
        ...,
        min_length=1
    )


class PredictionResponse(BaseModel):

    assessment_id: int | None = None

    prediction: str

    risk_probability: float

    risk_score: float

    risk_level: str

    recommendation: str


class ReviewUpdate(BaseModel):

    review_status: str = Field(
        ...,
        pattern="^(PENDING|REVIEWED)$"
    )

    reviewer_note: str = Field(
        default="",
        max_length=2000
    )