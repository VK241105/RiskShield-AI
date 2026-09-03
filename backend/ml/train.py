"""
RiskShield AI
Synthetic Return & Refund Risk Dataset Generator

IMPORTANT:
This dataset is SYNTHETIC and is intended for prototype/demo purposes.

The target is generated from observable customer and order behavior.
No target value is used as an input feature.

The goal is to create a realistic but learnable return-risk problem
for demonstrating an AI risk-management system.
"""

from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
N_SAMPLES = 15000

TARGET_RISK_RATE = 0.22

OUTPUT_FILE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "return_risk_dataset.csv"
)


# ============================================================
# RANDOM GENERATOR
# ============================================================

rng = np.random.default_rng(RANDOM_SEED)


# ============================================================
# CUSTOMER PROFILE
# ============================================================

customer_age = np.clip(
    rng.normal(32, 10, N_SAMPLES),
    18,
    70
).round().astype(int)


customer_account_age_days = np.clip(
    rng.gamma(3.0, 180, N_SAMPLES),
    15,
    2500
).round().astype(int)


previous_orders = np.clip(
    rng.poisson(12, N_SAMPLES),
    0,
    80
).astype(int)


# ============================================================
# CUSTOMER RETURN / REFUND HISTORY
# ============================================================

# Historical return behavior
previous_returns = np.minimum(
    previous_orders,
    rng.binomial(
        previous_orders,
        0.13
    )
).astype(int)


# Historical refund behavior
previous_refunds = np.minimum(
    previous_returns + 3,
    rng.binomial(
        np.maximum(previous_orders, 1),
        0.08
    )
).astype(int)


# ============================================================
# RECENT CUSTOMER ACTIVITY
# ============================================================

orders_last_30_days = np.clip(
    rng.poisson(
        2.5 + np.minimum(previous_orders, 15) * 0.08,
        N_SAMPLES
    ),
    0,
    20
).astype(int)


returns_last_90_days = np.clip(
    rng.poisson(
        0.7 + previous_returns * 0.10,
        N_SAMPLES
    ),
    0,
    12
).astype(int)


# ============================================================
# ORDER INFORMATION
# ============================================================

order_amount = np.clip(
    rng.lognormal(
        mean=7.0,
        sigma=0.65,
        size=N_SAMPLES
    ),
    150,
    50000
).round(2)


delivery_days = np.clip(
    rng.normal(4.5, 1.8, N_SAMPLES),
    1,
    14
).round(1)


discount_percentage = np.clip(
    rng.beta(2.0, 5.0, N_SAMPLES) * 70,
    0,
    70
).round(2)


# ============================================================
# CATEGORICAL INFORMATION
# ============================================================

payment_method = rng.choice(
    [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Cash on Delivery",
        "Wallet"
    ],
    size=N_SAMPLES,
    p=[
        0.35,
        0.25,
        0.20,
        0.15,
        0.05
    ]
)


product_category = rng.choice(
    [
        "Fashion",
        "Grocery",
        "Accessories",
        "Electronics",
        "Home"
    ],
    size=N_SAMPLES,
    p=[
        0.28,
        0.18,
        0.18,
        0.20,
        0.16
    ]
)


# ============================================================
# BEHAVIORAL FEATURES
# ============================================================

return_rate = (
    (previous_returns + returns_last_90_days)
    /
    np.maximum(
        previous_orders + orders_last_30_days,
        1
    )
)

return_rate = np.clip(
    return_rate,
    0,
    1
)


refund_rate = (
    previous_refunds
    /
    np.maximum(
        previous_orders,
        1
    )
)

refund_rate = np.clip(
    refund_rate,
    0,
    1
)


# ============================================================
# FEATURE ENGINEERING
# ============================================================

recent_return_ratio = (
    returns_last_90_days
    /
    np.maximum(
        orders_last_30_days + 2,
        2
    )
)

recent_return_ratio = np.clip(
    recent_return_ratio,
    0,
    1
)


refund_return_ratio = (
    previous_refunds
    /
    np.maximum(
        previous_returns,
        1
    )
)

refund_return_ratio = np.clip(
    refund_return_ratio,
    0,
    1
)


customer_activity_rate = (
    previous_orders
    /
    np.maximum(
        customer_account_age_days / 30,
        1
    )
)


average_order_value = (
    order_amount
    /
    np.maximum(
        previous_orders + 1,
        1
    )
)


# ============================================================
# LATENT RISK SCORE
#
# IMPORTANT:
# This score is ONLY used to generate the synthetic target.
# It is NOT included in the model features.
# ============================================================

risk_score = (

    # Strongest signal:
    3.0 * return_rate

    + 2.2 * refund_rate

    + 1.7 * recent_return_ratio

    + 1.2 * refund_return_ratio

    + 0.55 * np.log1p(orders_last_30_days)

    + 0.35 * np.log1p(previous_orders)

    + 0.30 * np.log1p(order_amount / 1000)

    + 0.45 * (discount_percentage / 100)

    + 0.35 * (delivery_days / 10)

    + 0.15 * customer_activity_rate

)


# ============================================================
# CATEGORY / PAYMENT RISK EFFECTS
# ============================================================

risk_score += np.where(
    product_category == "Fashion",
    0.30,
    0
)

risk_score += np.where(
    product_category == "Electronics",
    0.22,
    0
)

risk_score += np.where(
    payment_method == "Cash on Delivery",
    0.35,
    0
)

risk_score += np.where(
    payment_method == "Wallet",
    0.15,
    0
)


# ============================================================
# SMALL REALISTIC NOISE
# ============================================================

risk_score += rng.normal(
    0,
    0.18,
    N_SAMPLES
)


# ============================================================
# CREATE TARGET
# ============================================================

# Convert risk score into a probability.
risk_probability = 1 / (
    1 + np.exp(
        -(
            2.5 * (
                risk_score
                - np.median(risk_score)
            )
        )
    )
)


# Normalize to approximately the desired prevalence.
risk_probability = (
    risk_probability
    / np.mean(risk_probability)
    * TARGET_RISK_RATE
)

risk_probability = np.clip(
    risk_probability,
    0.01,
    0.95
)


return_risk = (
    rng.random(N_SAMPLES)
    < risk_probability
).astype(int)


# ============================================================
# CALIBRATE PREVALENCE
# ============================================================

# Keep approximately TARGET_RISK_RATE risky records.
target_count = int(
    N_SAMPLES * TARGET_RISK_RATE
)

current_count = int(
    return_risk.sum()
)


if current_count > target_count:

    risky_indices = np.where(
        return_risk == 1
    )[0]

    keep_indices = rng.choice(
        risky_indices,
        size=target_count,
        replace=False
    )

    return_risk[:] = 0

    return_risk[keep_indices] = 1


elif current_count < target_count:

    normal_indices = np.where(
        return_risk == 0
    )[0]

    add_count = target_count - current_count

    add_indices = rng.choice(
        normal_indices,
        size=add_count,
        replace=False
    )

    return_risk[add_indices] = 1


# ============================================================
# FINAL DATAFRAME
# ============================================================

df = pd.DataFrame({

    "customer_age": customer_age,

    "order_amount": order_amount,

    "previous_orders": previous_orders,

    "previous_returns": previous_returns,

    "previous_refunds": previous_refunds,

    "delivery_days": delivery_days,

    "discount_percentage": discount_percentage,

    "customer_account_age_days":
        customer_account_age_days,

    "orders_last_30_days":
        orders_last_30_days,

    "returns_last_90_days":
        returns_last_90_days,

    "return_rate":
        return_rate.round(4),

    "refund_rate":
        refund_rate.round(4),

    "recent_return_ratio":
        recent_return_ratio.round(4),

    "refund_return_ratio":
        refund_return_ratio.round(4),

    "customer_activity_rate":
        customer_activity_rate.round(4),

    "average_order_value":
        average_order_value.round(2),

    "payment_method":
        payment_method,

    "product_category":
        product_category,

    "return_risk":
        return_risk
})


# ============================================================
# SHUFFLE
# ============================================================

df = df.sample(
    frac=1,
    random_state=RANDOM_SEED
).reset_index(drop=True)


# ============================================================
# SAVE
# ============================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# DATASET REPORT
# ============================================================

print("=" * 70)
print("RISKSHIELD AI — DATASET GENERATION")
print("=" * 70)

print(
    f"\nDataset saved to:\n{OUTPUT_FILE}"
)

print(
    f"\nDataset shape: {df.shape}"
)

print("\nClass distribution:")

print(
    df["return_risk"]
    .value_counts()
    .sort_index()
)

print("\nClass percentages:")

print(
    df["return_risk"]
    .value_counts(
        normalize=True
    )
    .sort_index()
    .mul(100)
    .round(2)
)

print("\nMissing values:")

print(
    df.isnull()
    .sum()
    .sum()
)

print("\nDuplicate rows:")

print(
    df.duplicated()
    .sum()
)

print("\nRiskShield dataset generation completed.")
print("IMPORTANT: This is SYNTHETIC prototype data.")
print("=" * 70)