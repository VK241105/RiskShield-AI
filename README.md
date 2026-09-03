# RiskShield AI

## AI-Powered Return & Refund Risk Management System

RiskShield AI is a defense-only AI risk management system designed to help e-commerce merchants identify potentially high-risk return/refund cases before they are processed.

The system analyzes customer and order information, calculates a risk probability and risk score, classifies the case into a risk level, and provides a recommendation for further action.

> **Important:** RiskShield AI is an independent engineering prototype developed for a hackathon. It is designed for defensive fraud/risk detection and does not automatically reject customers, deny refunds, or make final business decisions.

---

## Demo

### Local Demo

The application currently runs locally using the Vite development server.

**Frontend:**

```text
http://localhost:5175/
```

**Backend API:**

```text
http://127.0.0.1:8000/
```

**Backend Health Check:**

```text
http://127.0.0.1:8000/health
```

> **Note:** `localhost` links are local development links and can only be accessed from the computer running the application.

### Public Demo

A public demo link will be added after deployment.

---

## GitHub Repository

```text
https://github.com/VK241105/RiskShield-AI/
```

---

## Overview

E-commerce businesses can face financial losses from suspicious return and refund activity. Manually checking every transaction can be time-consuming and may lead to inconsistent decisions.

RiskShield AI provides an AI-assisted risk assessment workflow.

The system:

* Collects customer and order information
* Calculates useful behavioral indicators
* Uses a trained machine learning model to estimate risk
* Generates a risk probability
* Converts the probability into a 0–100 risk score
* Classifies the case as **LOW**, **MEDIUM**, or **HIGH**
* Provides an actionable recommendation
* Supports human review of high-risk cases

The goal is to help merchants **prioritize cases that require additional attention** while keeping the final decision with a human reviewer.

---

## Key Features

### 1. Return/Refund Risk Prediction

The system predicts whether a return/refund case should be considered potentially high risk.

### 2. Risk Probability

The machine learning model produces a probability representing the estimated risk.

### 3. Risk Score

The probability is converted into a simple score between:

```text
0 – 100
```

Higher scores indicate higher estimated risk.

### 4. Risk Classification

Risk is classified into three levels:

| Risk Score | Risk Level |
| ---------- | ---------- |
| 0–29       | LOW        |
| 30–59      | MEDIUM     |
| 60–100     | HIGH       |

### 5. Recommendation

The system provides a recommendation based on the predicted risk:

* **LOW:** Normal processing
* **MEDIUM:** Additional verification recommended
* **HIGH:** Manual review recommended

### 6. Human-in-the-Loop

RiskShield AI does not make the final business decision automatically.

High-risk cases can be reviewed by a human decision-maker.

### 7. React Dashboard

The frontend provides a simple interface for entering customer/order information and viewing the resulting risk assessment.

---

## Core Workflow

```text
Customer / Order Information
            ↓
     Frontend Validation
            ↓
       FastAPI Backend
            ↓
   Feature Engineering
            ↓
   Random Forest Model
            ↓
     Risk Probability
            ↓
       Risk Score 0–100
            ↓
     Risk Classification
            ↓
       Recommendation
            ↓
      Human Review
```

---

## System Architecture

```text
┌──────────────────────────────┐
│       React Frontend         │
│      Vite + React + CSS      │
└──────────────┬───────────────┘
               │
               │ HTTP Request
               ↓
┌──────────────────────────────┐
│       FastAPI Backend        │
│        /predict API          │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│     Feature Engineering      │
│ Return Rate                  │
│ Refund Rate                  │
│ Recent Return Ratio          │
│ Customer Activity Rate       │
│ Average Order Value          │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│     Random Forest Model      │
│ riskshield_model.joblib      │
└──────────────┬───────────────┘
               │
               ↓
┌──────────────────────────────┐
│       Risk Assessment        │
│ Probability                  │
│ Score                        │
│ Risk Level                   │
│ Recommendation               │
└──────────────────────────────┘
```

---

## Project Structure

The current project structure is:

```text
RiskShield-AI/
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── predictor.py
│   │   └── schemas.py
│   │
│   └── ml/
│       ├── generate_dataset.py
│       ├── train.py
│       ├── compare_models.py
│       ├── tune_threshold.py
│       ├── save_final_model.py
│       └── evaluate.py
│
├── data/
│   └── return_risk_dataset.csv
│
├── models/
│   ├── riskshield_model.joblib
│   └── risk_threshold.joblib
│
├── frontend/
│   ├── public/
│   │
│   ├── src/
│   │   ├── components/
│   │   │   └── Navbar.jsx
│   │   │
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   └── RiskAnalysis.jsx
│   │   │
│   │   ├── api.js
│   │   ├── App.css
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── package-lock.json
│   ├── vite.config.js
│   └── index.html
│
├── .gitignore
└── README.md
```

> `node_modules/` and production build files are not included in the repository structure because they are generated dependencies/build artifacts and should be ignored by Git.

---

## File Responsibilities

### Backend

#### `backend/app/main.py`

Main FastAPI application.

Responsible for:

* Starting the API server
* Defining API endpoints
* Receiving prediction requests
* Returning risk assessment results

#### `backend/app/predictor.py`

Handles the machine learning prediction process.

Responsible for:

* Loading the trained model
* Creating engineered features
* Calculating risk probability
* Applying the selected threshold
* Generating risk level
* Generating recommendation

#### `backend/app/schemas.py`

Defines the request and response data structures used by the FastAPI API.

---

## Machine Learning

RiskShield AI currently uses a **Random Forest classifier** for return/refund risk prediction.

### Input Features

The model receives customer and order information including:

* Customer age
* Order amount
* Previous orders
* Previous returns
* Previous refunds
* Delivery days
* Discount percentage
* Customer account age
* Orders in the last 30 days
* Returns in the last 90 days
* Payment method
* Product category

### Engineered Features

Additional behavioral features are calculated from the input data:

* Return rate
* Refund rate
* Recent return ratio
* Refund-to-return ratio
* Customer activity rate
* Average order value

These features provide the model with additional information about customer ordering and return behavior.

---

## Risk Calculation

The trained model generates a probability using `predict_proba`.

The probability is converted into a risk score:

```text
Risk Score = Risk Probability × 100
```

The system then classifies the score using the configured thresholds.

```text
Score < 30
    ↓
LOW RISK

30 ≤ Score < 60
    ↓
MEDIUM RISK

Score ≥ 60
    ↓
HIGH RISK
```

The risk threshold is stored separately in:

```text
models/risk_threshold.joblib
```

This allows the selected threshold from the model evaluation process to be reused during prediction.

---

## Machine Learning Pipeline

The ML workflow contains several stages:

### 1. Dataset Generation

```text
backend/ml/generate_dataset.py
```

Generates the dataset used for the prototype.

### 2. Model Training

```text
backend/ml/train.py
```

Trains the machine learning model.

### 3. Model Comparison

```text
backend/ml/compare_models.py
```

Used to compare candidate machine learning approaches.

### 4. Threshold Tuning

```text
backend/ml/tune_threshold.py
```

Used to identify an appropriate decision threshold based on model evaluation.

### 5. Final Model Saving

```text
backend/ml/save_final_model.py
```

Saves the final trained model for use by the backend.

### 6. Model Evaluation

```text
backend/ml/evaluate.py
```

Evaluates the model on the available test data.

---

## API

The backend is built using **FastAPI**.

### Base URL

```text
http://127.0.0.1:8000
```

### Health Check

```http
GET /health
```

Used to check whether the backend is running.

### Prediction

```http
POST /predict
```

The frontend sends customer and order information to this endpoint.

### Example Request

```json
{
  "customer_age": 28,
  "order_amount": 2499,
  "previous_orders": 12,
  "previous_returns": 4,
  "previous_refunds": 3,
  "delivery_days": 4,
  "discount_percentage": 15,
  "customer_account_age_days": 420,
  "orders_last_30_days": 3,
  "returns_last_90_days": 2,
  "payment_method": "Credit Card",
  "product_category": "Electronics"
}
```

### Example Response

```json
{
  "prediction": 1,
  "risk_probability": 0.72,
  "risk_score": 72,
  "risk_level": "HIGH",
  "recommendation": "Manual review recommended"
}
```

---

## Technology Stack

### Frontend

* React.js
* Vite
* JavaScript
* JSX
* CSS
* React Router

### Backend

* Python
* FastAPI
* Pydantic
* Uvicorn

### Machine Learning

* scikit-learn
* Random Forest
* pandas
* NumPy
* Joblib

### Data

* CSV-based prototype dataset
* Synthetic return/refund risk data

---

## Installation

### Prerequisites

Make sure the following are installed:

* Python
* Node.js
* npm
* Git

---

## Backend Setup

Open a terminal in the project root.

Create/activate the Python virtual environment if it already exists:

### Windows PowerShell

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the backend dependencies required by the project.

Then start the FastAPI server:

```powershell
uvicorn backend.app.main:app --reload
```

The backend should be available at:

```text
http://127.0.0.1:8000
```

Check:

```text
http://127.0.0.1:8000/health
```

---

## Frontend Setup

Open another terminal.

Move into the frontend directory:

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the Vite development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5175/
```

> Vite may use another available port if `5175` is already occupied. Always open the URL displayed in the terminal.

---

## Running the Complete Application

You need **two terminals**.

### Terminal 1 — Backend

From the project root:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

### Terminal 2 — Frontend

```powershell
cd frontend
npm run dev
```

Then open the frontend URL shown by Vite.

Currently:

```text
http://localhost:5175/
```

---

## Production Build

To create a production build of the frontend:

```powershell
cd frontend
npm run build
```

The production files are generated inside:

```text
frontend/dist/
```

To preview the production build locally:

```powershell
npm run preview
```

---

## Model Evaluation

The project includes a model evaluation workflow using a held-out test set.

The current prototype evaluation achieved approximately:

```text
Accuracy: 76.22%
```

at the selected/locked risk threshold.

> These results are prototype evaluation results based on the project's dataset. They should not be interpreted as production fraud-detection performance.

For a production system, evaluation should include additional metrics such as:

* Precision
* Recall
* F1-score
* ROC-AUC
* Confusion matrix
* False-positive rate
* False-negative rate

This is particularly important for risk systems because incorrectly flagging legitimate customers can create a poor customer experience.

---

## Dataset

The current prototype uses a **synthetic dataset** for development and evaluation.

The dataset is located at:

```text
data/return_risk_dataset.csv
```

Synthetic data is useful for demonstrating the engineering workflow without exposing real customer information.

However, synthetic data cannot fully represent real-world customer behavior.

A production system would require:

* Real historical transaction data
* Properly labeled outcomes
* Privacy-compliant data collection
* Bias and fairness evaluation
* Continuous monitoring
* Regular model validation

---

## Responsible Use

RiskShield AI is designed as a **defensive risk-assistance system**.

The system should be used to:

* Identify potentially suspicious cases
* Prioritize cases for review
* Assist fraud/risk teams
* Reduce manual screening effort
* Provide consistent risk indicators

The system should **not** be used as the sole basis for:

* Automatically rejecting customers
* Automatically denying legitimate refunds
* Permanently blocking customers
* Making decisions based on protected characteristics

Final actions should remain subject to appropriate human review and business policies.

---

## Limitations

This project is a hackathon/engineering prototype and has several limitations.

### Synthetic Data

The model is trained and evaluated using synthetic data, so its performance may differ significantly from performance on real-world data.

### Limited Features

Real-world return/refund risk may depend on many additional signals that are not included in the current prototype.

### Model Generalization

A model trained on one dataset may not perform equally well across different merchants, products, countries, or customer populations.

### Human Review

The system provides recommendations rather than replacing human decision-making.

### Production Security

Additional security, authentication, rate limiting, monitoring, logging, and production CORS configuration would be required before real-world deployment.

---

## Future Scope

Potential improvements include:

* Integration with real e-commerce transaction systems
* More advanced machine learning models
* Explainable AI for individual risk predictions
* Real-time transaction monitoring
* Anomaly detection
* Behavioral sequence analysis
* Model drift monitoring
* Feedback-based model retraining
* Multi-merchant risk adaptation
* Advanced fraud pattern detection
* Role-based access control
* Production-grade authentication and security
* More extensive fairness and bias testing

---

## Public Deployment

The current application is designed for local development.

For a public demo, the system can be deployed using:

```text
Frontend
   ↓
Vercel / Netlify / Similar Platform
   ↓
FastAPI Backend
   ↓
Cloud Backend Platform
```

## GitHub

The project repository is:

```text
https://github.com/VK241105/RiskShield-AI/
```

## Project Goal

RiskShield AI demonstrates how machine learning can be integrated into an e-commerce risk-management workflow to identify potentially high-risk return/refund cases.

The project focuses on:

**Detection → Risk Scoring → Prioritization → Human Review**

rather than automatic rejection or denial of legitimate customers.

---

## Status

**Current Status:** Working prototype

**Frontend:** React + Vite

**Backend:** FastAPI

**ML Model:** Random Forest

**Data:** Synthetic prototype dataset

**Risk Output:** Probability + Score + Risk Level + Recommendation

**Local Frontend:** `http://localhost:5175/`

**Local Backend:** `http://127.0.0.1:8000/`


