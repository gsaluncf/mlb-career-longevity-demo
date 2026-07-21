# ⚾ MLB Career Longevity Predictor

**Avery Bishop** · Distributed Systems for Data Science · New College of Florida · Spring 2026

## Working Demo

The checked-in Streamlit app now runs as a self-contained demonstration. It
loads `sdm2_cum_inj.csv` locally, caches the prepared player-season data with
Streamlit, and displays the dataset's recorded `years_left` output. It does not
require AWS credentials, an EC2 API, S3 access, or the original model artifact.

The original deployment URL was:
[MLB Career Longevity Predictor](https://averybishop-mlb-career-predictor-app.streamlit.app/)

## What It Predicts
Given an MLB position player's name, the demonstration retrieves their career
history from the bundled dataset and displays the precomputed `years_left`
output along with performance and injury charts.

## Run Locally

```powershell
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Try `Mike Trout` or another position player present in the dataset.

## Deploy on Streamlit Community Cloud

1. Push this repository to GitHub.
2. In Streamlit Community Cloud, create an app from the repository.
3. Select `app.py` as the entry point and deploy.

No secrets are required. Ensure `app.py`, `mlb_data.py`, `requirements.txt`, and
`sdm2_cum_inj.csv` are committed to the repository.

## Original Student Pipeline Architecture

The following describes the original distributed project. The working demo
uses the cached local path described above.

```text
Raw Data (GitHub CSV)
↓
S3 (Bronze Layer — raw CSV storage)
↓
Databricks + PySpark (Silver — cleaned, typed, validated)
↓
Databricks + PySpark (Gold — feature table, nulls removed)
↓
MLflow (Model training, experiment tracking, model registry)
↓
S3 (Model artifact + gold CSV storage)
↓
EC2 FastAPI (Live prediction endpoint)
↓
Streamlit Cloud (Public web application)
```

## Tech Stack
| Layer | Technology |
|---|---|
| Raw Storage | AWS S3 |
| Transformation | Databricks PySpark (silver/gold medallion) |
| ML Training | scikit-learn Random Forest + Databricks MLflow |
| Model Serving | FastAPI on AWS EC2 (t3.micro) |
| Frontend | Streamlit Cloud |

## Model Performance
- **Algorithm:** Random Forest Regressor (100 trees, max depth 10)
- **Target:** Years remaining in MLB career
- **MAE:** 2.53 years
- **R²:** 0.363
- **Training rows:** 47,991 player-seasons (1871–2024)

## Repository Structure
mlb-career-predictor/
├── app.py                        # Streamlit frontend
├── api.py                        # FastAPI backend (EC2)
├── mlb_data.py                   # Cached-demo data loading and lookup
├── tests/test_mlb_data.py        # Local data and lookup tests
├── testing_app.py                # Original external API test script
├── requirements.txt              # Streamlit dependencies
├── sdm2_cum_inj.csv             # Raw dataset (bronze layer)
├── mlb_career_predictions.ipynb  # Databricks pipeline notebook
└── README.md

## Running the Self-Contained Tests
```bash
python -m pytest -v
```

The tests verify local CSV loading, case-insensitive player lookup,
same-name player selection, missing-data handling, and a real Mike Trout lookup.

## Notes
- `testing_app.py` and `api.py` are retained as original project artifacts; they
  are not used by the self-contained Streamlit demo.
- AWS credentials in `api.py` and the Databricks notebook have been replaced with placeholders
- Databricks Community Edition restrictions prevented Delta Lake persistence and direct S3 mounting — the medallion architecture is implemented via in-memory Spark DataFrames with S3 used for bronze storage and model/data artifact export
