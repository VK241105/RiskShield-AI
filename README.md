# RiskShield AI

RiskShield AI is a defense-only return and refund risk-management system. It
helps merchants identify potentially risky cases before avoidable losses occur,
while keeping the final decision with an authorized human reviewer.

This is an independent fintech engineering prototype. It is not a payment
processor or a copy of any payment company. The included model uses synthetic
data, so the displayed metrics demonstrate the evaluation workflow and are not
production performance claims.

## Demo

Local demo URL: http://localhost:5173

The local demo requires both services to be running. A public demo link cannot
be created from localhost; the backend and frontend must be deployed to hosted
services first. After deployment, set `VITE_API_URL` to the public backend URL
before building the frontend.

## Core Workflow

1. Enter customer and order information.
2. Select the account creation date; account age is calculated automatically.
3. Submit the case to receive a risk probability, score, level, and recommendation.
4. Review the saved case and full input data from Recent Assessments.
5. Add a human-review note and mark the assessment reviewed.
6. Delete one record, clear all records, or export the history as CSV.

## Architecture

```text
React/Vite dashboard -> FastAPI /predict -> Random Forest model
                                      -> risk score and review recommendation
                                      -> SQLite assessment history and audit events
```

## Project Structure

- `frontend/`: React operator dashboard
- `backend/app/`: FastAPI API, validation, prediction, SQLite storage, audit events
- `backend/ml/`: reproducible dataset and model training/evaluation scripts
- `data/return_risk_dataset.csv`: synthetic prototype dataset
- `models/`: active model and locked threshold used by the API

## Run Locally

From the repository root, start the backend:

```powershell
.\.venv\Scripts\Activate.ps1
uvicorn backend.app.main:app --reload
```

In another terminal, start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

Open http://localhost:5173.

## API

- `GET /health`: service and model readiness
- `POST /predict`: calculate and save an assessment
- `GET /assessments`: list saved assessments
- `PATCH /assessments/{id}/review`: update human-review status and note
- `DELETE /assessments/{id}`: delete one assessment
- `DELETE /assessments`: clear assessment history

Assessment data is stored locally in `data/riskshield.db`, which is ignored by
Git. Do not use this SQLite prototype with sensitive customer data.

## Evaluation

The model evaluation script reports accuracy, precision, recall, F1, ROC-AUC,
PR-AUC, confusion matrix, and business cost on a held-out test set. The current
prototype accuracy is approximately 76%, and the model should not be judged by
accuracy alone because false positives and false negatives have different costs.

## Public Deployment

For a public demo, deploy the backend and frontend separately. Configure the
backend `RISKSHIELD_ALLOWED_ORIGINS` with the frontend URL, then configure the
frontend build variable:

```text
VITE_API_URL=https://your-backend.example.com
```

A production deployment also needs authentication, HTTPS, encrypted or managed
database storage, backups, rate limiting, monitoring, privacy review, and real
consented labeled data.
