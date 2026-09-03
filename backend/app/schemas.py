from pydantic import BaseModel, Field


class OrderData(BaseModel):

    customer_age: float = Field(..., ge=18)
    order_amount: float = Field(..., ge=0)

    previous_orders: int = Field(..., ge=0)
    previous_returns: int = Field(..., ge=0)
    previous_refunds: int = Field(..., ge=0)

    delivery_days: float = Field(..., ge=0)
    discount_percentage: float = Field(..., ge=0, le=100)

    customer_account_age_days: int = Field(..., ge=0)

    orders_last_30_days: int = Field(..., ge=0)
    returns_last_90_days: int = Field(..., ge=0)

    return_rate: float = Field(..., ge=0, le=1)
    refund_rate: float = Field(..., ge=0, le=1)

    payment_method: str
    product_category: str


class PredictionResponse(BaseModel):

    prediction: str
    risk_probability: float
    risk_score: float
    risk_level: str
    recommendation: str
    