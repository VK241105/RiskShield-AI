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
                                    # RiskShield AI

                                    RiskShield AI is a defense-only return and refund risk-management system. It
                                    helps a merchant identify potentially risky cases before avoidable losses occur
                                    while keeping the final decision with an authorized human reviewer.

                                    This is an independent fintech engineering prototype. It is not a payment
                                    processor and does not automatically reject customers or approve refunds. The
                                    included model uses synthetic data, so its metrics demonstrate the evaluation
                                    workflow and are not production performance claims.

                                    ## What The System Does

                                    The application accepts customer and order signals, runs a trained machine
                                    learning model, and returns:

                                    - Risk probability
                                    - Risk score from 0 to 100
                                    - Low, Medium, or High risk level
                                    - Normal processing, verification, or manual-review recommendation
                                    - Persistent assessment history
                                    - Human-review status and reviewer notes

                                    ## End-to-End Sequence

                                    ```text
                                    1. User opens the React dashboard
                                        |
                                    2. User enters customer, account, return, refund, and order data
                                        |
                                    3. Frontend validates values and calculates account age from creation date
                                        |
                                    4. Frontend sends POST /predict to FastAPI
                                        |
                                    5. Pydantic validates the request against OrderData
                                        |
                                    6. Predictor adds engineered behavior features
                                        |
                                    7. Random Forest model calculates risk probability
                                        |
                                    8. Locked threshold and score rules produce the risk result
                                        |
                                    9. Backend saves order data, result, and audit event in SQLite
                                        |
                                    10. Frontend navigates to Risk Analysis and displays the result
                                        |
                                    11. Reviewer can inspect, annotate, mark reviewed, export, or delete it
                                    ```

                                    ## Project Structure

                                    ```text
                                    RiskShield-AI/
                                    |
                                    |-- backend/
                                    |   |-- app/
                                    |   |   |-- main.py
                                    |   |   |-- database.py
                                    |   |   |-- predictor.py
                                    |   |   |-- schemas.py
                                    |   |
                                    |   |-- ml/
                                    |       |-- generate_dataset.py
                                    |       |-- train.py
                                    |       |-- compare_models.py
                                    |       |-- tune_threshold.py
                                    |       |-- save_final_model.py
                                    |       |-- evaluate.py
                                    |
                                    |-- data/
                                    |   |-- return_risk_dataset.csv
                                    |   |-- riskshield.db                 # local runtime database, ignored by Git
                                    |
                                    |-- models/
                                    |   |-- riskshield_model.joblib       # active prediction pipeline
                                    |   |-- risk_threshold.joblib         # locked decision threshold
                                    |
                                    |-- frontend/
                                    |   |-- index.html
                                    |   |-- package.json
                                    |   |-- package-lock.json
                                    |   |-- vite.config.js
                                    |   |-- .env.example
                                    |   |-- src/
                                    |       |-- main.jsx
                                    |       |-- App.jsx
                                    |       |-- api.js
                                    |       |-- App.css
                                    |       |-- index.css
                                    |       |-- components/
                                    |       |   |-- Navbar.jsx
                                    |       |-- pages/
                                    |           |-- Dashboard.jsx
                                    |           |-- RiskAnalysis.jsx
                                    |
                                    |-- .gitignore
                                    |-- README.md
                                    ```

                                    ## File Responsibilities

                                    ### Frontend

                                    `frontend/src/main.jsx` is the browser entrypoint. It mounts the React app.

                                    `frontend/src/App.jsx` owns routing, latest-result state, persistent fallback
                                    history, and the live backend health indicator. It exposes only the two core
                                    screens: Dashboard and Risk Analysis.

                                    `frontend/src/api.js` contains the configurable backend URL. Local development
                                    defaults to `http://127.0.0.1:8000`; hosted deployments use `VITE_API_URL`.

                                    `frontend/src/components/Navbar.jsx` provides the focused product navigation.

                                    `frontend/src/pages/Dashboard.jsx` contains the assessment form, date-based
                                    account-age calculation, client-side consistency checks, demo case loader,
                                    assessment history, CSV export, deletion, and human-review modal.

                                    `frontend/src/pages/RiskAnalysis.jsx` renders the latest prediction, score,
                                    probability, recommendation, interpretation, and human-review reminder.

                                    `frontend/src/App.css` contains the application layout and responsive design.
                                    `frontend/src/index.css` contains the global reset and base browser styles.

                                    ### Backend

                                    `backend/app/main.py` creates the FastAPI service, configures restricted CORS,
                                    adds security headers, initializes the database, and defines the API routes.

                                    `backend/app/schemas.py` defines Pydantic request/response contracts. It checks
                                    numeric ranges, required fields, review status, and reviewer-note length.

                                    `backend/app/predictor.py` loads the active model and threshold, computes
                                    engineered features, generates probability and score, and maps the score to a
                                    risk level and recommendation.

                                    `backend/app/database.py` owns SQLite connections, assessment persistence,
                                    review updates, deletion, and append-only audit events.

                                    ### Machine Learning

                                    `backend/ml/generate_dataset.py` creates the synthetic prototype dataset.

                                    `backend/ml/train.py` trains a baseline model.

                                    `backend/ml/compare_models.py` compares candidate classifiers on validation and
                                    test splits.

                                    `backend/ml/tune_threshold.py` selects a threshold using validation data and
                                    business costs without using the held-out test set for selection.

                                    `backend/ml/save_final_model.py` trains and saves the production pipeline.

                                    `backend/ml/evaluate.py` reports final held-out accuracy, precision, recall, F1,
                                    ROC-AUC, PR-AUC, confusion matrix, and false-positive/false-negative cost.

                                    ## Local Run

                                    From the repository root, start the backend:

                                    ```powershell
                                    .\.venv\Scripts\Activate.ps1
                                    uvicorn backend.app.main:app --reload
                                    ```

                                    In a second terminal, start the frontend:

                                    ```powershell
                                    Set-Location frontend
                                    npm install
                                    npm run dev
                                    ```

                                    Open http://localhost:5173.

                                    ## API Routes

                                    - `GET /`: API identity and running status
                                    - `GET /health`: backend, model, and threshold readiness
                                    - `POST /predict`: validate, predict, persist, and return an assessment
                                    - `GET /assessments`: list saved assessments
                                    - `PATCH /assessments/{id}/review`: save review status and note
                                    - `DELETE /assessments/{id}`: delete one assessment and audit the action
                                    - `DELETE /assessments`: clear all assessments and audit deletions

                                    ## Storage And Security

                                    Assessment data is stored locally in `data/riskshield.db`. Each assessment
                                    contains the submitted model inputs, result, review status, reviewer note, and
                                    creation timestamp. Audit events record assessment creation, review updates,
                                    and deletion.

                                    The database, virtual environment, build output, Node dependencies, and `.env`
                                    files are ignored by Git. The API uses restricted configurable CORS and adds
                                    basic security headers. This local SQLite setup is suitable for demonstration,
                                    not sensitive production customer data.

                                    ## Evaluation

                                    The current prototype is evaluated on a held-out test set. Its verified accuracy
                                    is approximately 76.22% at the locked threshold. The system also reports
                                    precision, recall, F1, ROC-AUC, PR-AUC, and error cost because accuracy alone can
                                    hide missed risky cases and unnecessary customer friction.

                                    ## Public Demo

                                    `localhost` is reachable only from the local computer. To give others a usable
                                    link, deploy the backend and frontend to hosted services.

                                    For the frontend build, configure:

                                    ```text
                                    VITE_API_URL=https://your-public-backend.example.com
                                    ```

                                    For the backend, configure:

                                    ```text
                                    RISKSHIELD_ALLOWED_ORIGINS=https://your-public-frontend.example.com
                                    ```

                                    A real deployment also needs authentication, role-based access, HTTPS,
                                    encrypted or managed database storage, backups, rate limiting, monitoring,
                                    privacy review, and consented real labeled data.

                                    ## Honest Project Positioning

                                    > RiskShield AI is a defense-only return and refund risk scorer that helps
                                    > merchants identify potentially risky cases before avoidable losses occur,
                                    > while keeping final decisions with authorized human reviewers.
