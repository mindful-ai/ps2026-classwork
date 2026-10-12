# Phase 6 — ML-Ready Dataset

This is the final phase of the six-phase data engineering project. It converts the trusted Gold `customer_features.parquet` table into a clean hand-off for downstream ML work.

## Scope

- Select the ML source table
- Separate identifiers from features
- Engineer date-derived features
- Encode categorical features
- Handle remaining missing values
- Validate the final feature matrix
- Export Parquet and CSV
- Generate a feature dictionary and validation report

No model training is performed here. This phase ends at the Data Engineering → ML hand-off.

## Input

```text
data/gold/customer_features.parquet
```

## Output

```text
data/ml_ready/
├── customer_ml_ready.parquet
├── customer_ml_ready.csv
└── feature_dictionary.json
```

Validation report:

```text
reports/ml/ml_ready_report.json
```

## Feature engineering

`customer_tenure_days` is derived from first and last order dates.

`recency_days` is the number of days from the latest order in the dataset to each customer's last order.

`segment`, `region`, and `favorite_category` are converted to numeric indicator columns with one-hot encoding.

`customer_id` is retained only as an identifier and is not part of the model feature matrix.

## Quality gate

The final dataset must be non-empty, have unique customer IDs, contain no missing values, contain only numeric model features, and have valid positive order/unit measures and non-negative spend.

## Run

```bash
python src/build_ml_ready.py
python src/inspect_ml_ready.py
pytest -q src/test_phase6.py
```

## ML hand-off

```python
import pandas as pd

df = pd.read_parquet('data/ml_ready/customer_ml_ready.parquet')
X = df.drop(columns=['customer_id'])
```

The downstream ML workflow can now perform its own train/validation/test split and model-specific preprocessing.

## Final six-phase architecture

```text
PHASE 1  Data & SQL Foundations
          ↓
PHASE 2  Data Quality & Trust
          ↓
PHASE 3  Storage & Formats
          ↓
PHASE 4  Bronze → Silver → Gold
          ↓
PHASE 5  Production Practices
          ↓
PHASE 6  ML-Ready Dataset
```

The final deliverable is `data/ml_ready/customer_ml_ready.parquet`.
