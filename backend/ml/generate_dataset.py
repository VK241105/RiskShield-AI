"""
RiskShield AI
Synthetic Return/Refund Risk Dataset Generator

Purpose:
Generate realistic-looking synthetic e-commerce order data for
prototype/model development.

IMPORTANT:
- This is synthetic data only.
- It does NOT represent real customer or merchant behavior.
- The hidden risk profile is used only during generation.
- The hidden risk profile is NOT included in the final dataset.
"""

import os
import numpy as np
import pandas as pd


# ============================================================
# CONFIGURATION
# ============================================================

RANDOM_SEED = 42
N_RECORDS = 15000

OUTPUT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "data")
)

OUTPUT_FILE = os.path.join(
    OUTPUT_DIR,
    "return_risk_dataset.csv"
)

np.random.seed(RANDOM_SEED)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def clip_int(values, minimum, maximum):
    """Clip values and convert them to integers."""
    return np.clip(np.round(values), minimum, maximum).astype(int)


def generate_beta_scaled(alpha, beta, minimum, maximum, size):
    """Generate values from a beta distribution and scale them."""
    values = np.random.beta(alpha, beta, size)
    return minimum + values * (maximum - minimum)


# ============================================================
# GENERATE HIDDEN RISK PROFILE
# ============================================================

def generate_hidden_risk_profile(n):
    """
    Generate a hidden behavioral risk state.

    0 = normal behavioral profile
    1 = elevated-risk behavioral profile

    This variable is NOT saved in the final dataset.
    """

    # Approximately 20% of orders originate from higher-risk profiles.
    return np.random.binomial(
        1,
        0.20,
        n
    )


# ============================================================
# MAIN DATASET GENERATION
# ============================================================

def generate_dataset():

    print("=" * 60)
    print("RISKSHIELD AI — DATASET GENERATION")
    print("=" * 60)

    print("\nGenerating synthetic customer/order behavior...")

    n = N_RECORDS

    # --------------------------------------------------------
    # Hidden risk profile
    # --------------------------------------------------------

    hidden_risk = generate_hidden_risk_profile(n)

    normal_mask = hidden_risk == 0
    risky_mask = hidden_risk == 1

    # --------------------------------------------------------
    # Customer age
    # --------------------------------------------------------

    customer_age = np.empty(n)

    customer_age[normal_mask] = np.random.normal(
        loc=34,
        scale=9,
        size=normal_mask.sum()
    )

    customer_age[risky_mask] = np.random.normal(
        loc=29,
        scale=8,
        size=risky_mask.sum()
    )

    customer_age = clip_int(
        customer_age,
        18,
        70
    )

    # --------------------------------------------------------
    # Customer account age
    # --------------------------------------------------------

    customer_account_age_days = np.empty(n)

    customer_account_age_days[normal_mask] = np.random.gamma(
        shape=3.5,
        scale=250,
        size=normal_mask.sum()
    )

    customer_account_age_days[risky_mask] = np.random.gamma(
        shape=2.2,
        scale=170,
        size=risky_mask.sum()
    )

    customer_account_age_days = clip_int(
        customer_account_age_days,
        15,
        3000
    )

    # --------------------------------------------------------
    # Previous orders
    # --------------------------------------------------------

    previous_orders = np.empty(n)

    previous_orders[normal_mask] = np.random.poisson(
        lam=8,
        size=normal_mask.sum()
    )

    previous_orders[risky_mask] = np.random.poisson(
        lam=6,
        size=risky_mask.sum()
    )

    previous_orders = np.clip(
        previous_orders,
        0,
        60
    ).astype(int)

    # --------------------------------------------------------
    # Previous returns
    #
    # Risky users have a significantly higher return behavior.
    # --------------------------------------------------------

    previous_return_rate_normal = np.random.beta(
        1.4,
        18,
        normal_mask.sum()
    )

    previous_return_rate_risky = np.random.beta(
        3.2,
        8,
        risky_mask.sum()
    )

    previous_returns = np.zeros(n, dtype=int)

    previous_returns[normal_mask] = np.minimum(
        np.random.binomial(
            previous_orders[normal_mask],
            previous_return_rate_normal
        ),
        previous_orders[normal_mask]
    )

    previous_returns[risky_mask] = np.minimum(
        np.random.binomial(
            previous_orders[risky_mask],
            previous_return_rate_risky
        ),
        previous_orders[risky_mask]
    )

    # --------------------------------------------------------
    # Previous refunds
    #
    # Refund behavior is related to previous returns but
    # contains additional randomness.
    # --------------------------------------------------------

    previous_refund_probability_normal = np.random.beta(
        1.2,
        25,
        normal_mask.sum()
    )

    previous_refund_probability_risky = np.random.beta(
        2.8,
        10,
        risky_mask.sum()
    )

    previous_refunds = np.zeros(n, dtype=int)

    previous_refunds[normal_mask] = np.minimum(
        np.random.binomial(
            previous_orders[normal_mask],
            previous_refund_probability_normal
        ),
        previous_returns[normal_mask]
    )

    previous_refunds[risky_mask] = np.minimum(
        np.random.binomial(
            previous_orders[risky_mask],
            previous_refund_probability_risky
        ),
        previous_returns[risky_mask]
    )

    # --------------------------------------------------------
    # Orders in last 30 days
    # --------------------------------------------------------

    orders_last_30_days = np.empty(n)

    orders_last_30_days[normal_mask] = np.random.poisson(
        lam=2.2,
        size=normal_mask.sum()
    )

    orders_last_30_days[risky_mask] = np.random.poisson(
        lam=4.5,
        size=risky_mask.sum()
    )

    orders_last_30_days = np.clip(
        orders_last_30_days,
        0,
        20
    ).astype(int)

    # --------------------------------------------------------
    # Returns in last 90 days
    # --------------------------------------------------------

    returns_last_90_days = np.zeros(n, dtype=int)

    returns_last_90_days[normal_mask] = np.random.poisson(
        lam=0.6,
        size=normal_mask.sum()
    )

    returns_last_90_days[risky_mask] = np.random.poisson(
        lam=2.2,
        size=risky_mask.sum()
    )

    returns_last_90_days = np.clip(
        returns_last_90_days,
        0,
        12
    ).astype(int)

    # --------------------------------------------------------
    # Discount percentage
    #
    # Higher discounts slightly increase risk.
    # --------------------------------------------------------

    discount_percentage = np.empty(n)

    discount_percentage[normal_mask] = generate_beta_scaled(
        2.0,
        7.0,
        0,
        60,
        normal_mask.sum()
    )

    discount_percentage[risky_mask] = generate_beta_scaled(
        2.8,
        5.0,
        0,
        70,
        risky_mask.sum()
    )

    discount_percentage = np.round(
        discount_percentage,
        2
    )

    # --------------------------------------------------------
    # Order amount
    # --------------------------------------------------------

    order_amount = np.empty(n)

    order_amount[normal_mask] = np.random.lognormal(
        mean=np.log(1300),
        sigma=0.55,
        size=normal_mask.sum()
    )

    order_amount[risky_mask] = np.random.lognormal(
        mean=np.log(1450),
        sigma=0.60,
        size=risky_mask.sum()
    )

    order_amount = np.clip(
        order_amount,
        150,
        25000
    )

    order_amount = np.round(
        order_amount,
        2
    )

    # --------------------------------------------------------
    # Delivery days
    #
    # Delayed delivery slightly increases return probability.
    # --------------------------------------------------------

    delivery_days = np.empty(n)

    delivery_days[normal_mask] = np.random.normal(
        loc=3.2,
        scale=1.2,
        size=normal_mask.sum()
    )

    delivery_days[risky_mask] = np.random.normal(
        loc=4.2,
        scale=1.5,
        size=risky_mask.sum()
    )

    delivery_days = clip_int(
        delivery_days,
        1,
        10
    )

    # --------------------------------------------------------
    # Return rate
    #
    # Historical return behavior.
    # Small smoothing prevents extreme 0/1 values.
    # --------------------------------------------------------

    return_rate = (
        previous_returns + 0.5
    ) / (
        previous_orders + 1.0
    )

    # Add recent return behavior to make the feature more useful.
    return_rate = (
        0.75 * return_rate
        + 0.25 * (
            returns_last_90_days /
            (orders_last_30_days + 3)
        )
    )

    return_rate += np.random.normal(
        0,
        0.025,
        n
    )

    return_rate = np.clip(
        return_rate,
        0,
        1
    )

    return_rate = np.round(
        return_rate,
        4
    )

    # --------------------------------------------------------
    # Refund rate
    # --------------------------------------------------------

    refund_rate = (
        previous_refunds + 0.3
    ) / (
        previous_orders + 1.0
    )

    refund_rate += np.random.normal(
        0,
        0.02,
        n
    )

    refund_rate = np.clip(
        refund_rate,
        0,
        1
    )

    refund_rate = np.round(
        refund_rate,
        4
    )

    # --------------------------------------------------------
    # Payment method
    # --------------------------------------------------------

    payment_methods = [
        "UPI",
        "Credit Card",
        "Debit Card",
        "Net Banking",
        "Cash on Delivery"
    ]

    payment_method = np.random.choice(
        payment_methods,
        size=n,
        p=[
            0.38,
            0.24,
            0.16,
            0.08,
            0.14
        ]
    )

    # --------------------------------------------------------
    # Product category
    # --------------------------------------------------------

    product_categories = [
        "Electronics",
        "Fashion",
        "Home",
        "Beauty",
        "Grocery",
        "Accessories"
    ]

    product_category = np.random.choice(
        product_categories,
        size=n,
        p=[
            0.20,
            0.25,
            0.17,
            0.13,
            0.12,
            0.13
        ]
    )

    # ========================================================
    # CREATE LATENT RISK SCORE
    # ========================================================

    print("Creating behavioral risk labels...")

    # Normalize important behavioral signals.
    return_signal = np.clip(
        return_rate,
        0,
        1
    )

    refund_signal = np.clip(
        refund_rate,
        0,
        1
    )

    recent_return_signal = np.clip(
        returns_last_90_days / 6.0,
        0,
        1
    )

    recent_order_signal = np.clip(
        orders_last_30_days / 12.0,
        0,
        1
    )

    discount_signal = np.clip(
        discount_percentage / 70.0,
        0,
        1
    )

    delivery_signal = np.clip(
        (delivery_days - 2) / 7.0,
        0,
        1
    )

    refund_history_signal = np.clip(
        previous_refunds / (
            previous_orders + 1
        ),
        0,
        1
    )

    # --------------------------------------------------------
    # Weighted behavioral score
    # --------------------------------------------------------

    risk_score = (
        2.8 * return_signal
        + 2.5 * refund_signal
        + 2.0 * recent_return_signal
        + 1.2 * recent_order_signal
        + 0.8 * discount_signal
        + 0.7 * delivery_signal
        + 1.7 * refund_history_signal
    )

    # Add realistic uncertainty/noise.
    risk_score += np.random.normal(
        0,
        0.55,
        n
    )

    # Small category/payment effects.
    risk_score += np.where(
        product_category == "Fashion",
        0.15,
        0
    )

    risk_score += np.where(
        product_category == "Electronics",
        0.08,
        0
    )

    risk_score += np.where(
        payment_method == "Cash on Delivery",
        0.12,
        0
    )

    # Hidden profile gives the generator a stronger but not
    # perfectly deterministic behavioral relationship.
    risk_score += hidden_risk * 1.5

    # ========================================================
    # CONVERT SCORE INTO PROBABILITY
    # ========================================================

    # Standardize score.
    score_mean = np.mean(risk_score)
    score_std = np.std(risk_score)

    standardized_score = (
        risk_score - score_mean
    ) / (
        score_std + 1e-8
    )

    # Sigmoid.
    risk_probability = 1 / (
        1 + np.exp(
            -(
                1.45 * standardized_score
                - 1.55
            )
        )
    )

    # ========================================================
    # INITIAL TARGET
    # ========================================================

    return_risk = np.random.binomial(
        1,
        risk_probability,
        n
    )

    # ========================================================
    # ADD CONTROLLED LABEL NOISE
    # ========================================================

    # Flip around 3% of labels.
    # This prevents an unrealistically clean synthetic dataset.
    noise_rate = 0.03

    noise_mask = np.random.random(n) < noise_rate

    return_risk[noise_mask] = (
        1 - return_risk[noise_mask]
    )

    # ========================================================
    # CALIBRATE PREVALENCE
    # ========================================================

    # Target approximately 20–25% risky orders.
    target_min = 0.20
    target_max = 0.25

    current_rate = return_risk.mean()

    if current_rate < target_min or current_rate > target_max:

        # Use the hidden risk profile as a small additional
        # calibration mechanism.
        #
        # We rank orders by behavioral risk score and assign
        # approximately 22% risky labels while retaining noise.

        target_risky_count = int(
            n * 0.22
        )

        ranked_indices = np.argsort(
            risk_score
        )[::-1]

        calibrated_labels = np.zeros(
            n,
            dtype=int
        )

        calibrated_labels[
            ranked_indices[:target_risky_count]
        ] = 1

        # Add controlled label uncertainty.
        calibration_noise = (
            np.random.random(n) < 0.025
        )

        calibrated_labels[
            calibration_noise
        ] = 1 - calibrated_labels[
            calibration_noise
        ]

        return_risk = calibrated_labels

    # ========================================================
    # BUILD FINAL DATAFRAME
    # ========================================================

    df = pd.DataFrame({
        "customer_age": customer_age,
        "order_amount": order_amount,
        "previous_orders": previous_orders,
        "previous_returns": previous_returns,
        "previous_refunds": previous_refunds,
        "delivery_days": delivery_days,
        "discount_percentage": discount_percentage,
        "customer_account_age_days": customer_account_age_days,
        "orders_last_30_days": orders_last_30_days,
        "returns_last_90_days": returns_last_90_days,
        "return_rate": return_rate,
        "refund_rate": refund_rate,
        "payment_method": payment_method,
        "product_category": product_category,
        "return_risk": return_risk
    })

    # ========================================================
    # DATA QUALITY CHECKS
    # ========================================================

    # Remove accidental duplicate rows.
    df = df.drop_duplicates().reset_index(drop=True)

    # Ensure integer columns remain integers.
    integer_columns = [
        "customer_age",
        "previous_orders",
        "previous_returns",
        "previous_refunds",
        "delivery_days",
        "customer_account_age_days",
        "orders_last_30_days",
        "returns_last_90_days",
        "return_risk"
    ]

    for column in integer_columns:
        df[column] = df[column].astype(int)

    # ========================================================
    # SAVE DATASET
    # ========================================================

    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    # ========================================================
    # DISPLAY RESULTS
    # ========================================================

    risky_count = int(
        df["return_risk"].sum()
    )

    normal_count = len(df) - risky_count

    risky_percentage = (
        risky_count / len(df)
    ) * 100

    print("\n" + "=" * 60)
    print("RISKSHIELD AI DATASET CREATED SUCCESSFULLY")
    print("=" * 60)

    print(f"Records: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nCLASS DISTRIBUTION")
    print("-" * 40)
    print(f"Normal orders : {normal_count:,}")
    print(f"Risky orders  : {risky_count:,}")
    print(f"Risk percentage: {risky_percentage:.2f}%")

    print("\nFEATURES")
    print("-" * 40)

    for column in df.columns:
        print(f"- {column}")

    print("\nDATASET TYPE")
    print("-" * 40)
    print("Synthetic data for prototype/model development")
    print("NOT real customer or merchant data.")

    print("\nDATA QUALITY")
    print("-" * 40)
    print(f"Duplicate rows: {df.duplicated().sum()}")
    print(
        f"Missing values: {df.isna().sum().sum()}"
    )

    print("\nTARGET COUNTS")
    print("-" * 40)
    print(
        df["return_risk"]
        .value_counts()
        .sort_index()
        .rename({
            0: "Normal",
            1: "Risky"
        })
        .to_string()
    )

    print("\nSaved to:")
    print(OUTPUT_FILE)

    print("=" * 60)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    generate_dataset()