# MLflow Customer Model Training

Three independently launched training scripts use the same MLflow tracking URI and the same MLflow experiment by default.

## Scripts

- `train_customer_segmentation.py` — K-Means customer segmentation.
- `train_customer_spending.py` — Random Forest regression for historical aggregate `total_spend`.
- `train_customer_churn_proxy.py` — Random Forest classification using a recency-based proxy label.

## Important dataset note

The ML-ready customer dataset contains 2,000 rows and 33 columns, including `customer_id`, `total_spend`, `recency_days`, customer order statistics, and encoded segment/region/category fields.

It does **not** contain an observed churn label. Therefore, the churn script creates a demonstration proxy label: `recency_days >= 90` by default. The `recency_days` column is excluded from model inputs to avoid directly leaking the proxy definition into the features. This is not a validated business churn model; use a real churn outcome and an agreed prediction horizon for production.

The spending model predicts the dataset's historical aggregate `total_spend`, not future-period spend. It excludes `total_spend` and `average_order_value` from the features, because average order value is directly derived from spend. For a true forward-looking forecast, create a time-based target window and features available before that window.

## Setup

From the root of the project, install dependencies:

```powershell
python -m pip install -r mlflow_training/requirements.txt
```

Start a local MLflow tracking server in a separate terminal, from the project root:

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
```

Open `http://127.0.0.1:5000` to view the UI.

## Run each script independently

From the project root:

```powershell
python mlflow_training/train_customer_segmentation.py
python mlflow_training/train_customer_spending.py
python mlflow_training/train_customer_churn_proxy.py
```

Optional arguments include `--data`, `--tracking-uri`, and `--experiment-name`. Segmentation also accepts `--clusters`; churn proxy accepts `--recency-threshold-days`.

## One shared tracking URI

All scripts default to:

```text
http://127.0.0.1:5000
```

You can set the URI once using an environment variable and all scripts will use it:

```powershell
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
```

They also use the same experiment by default:

```text
data-engineering-with-astro-customer-ml
```

Each run logs parameters, metrics, model artifacts, dataset lineage, and a SHA-256 hash of the CSV. Segmentation also logs cluster assignments and profiles; regression logs feature importances; the churn-proxy script logs a classification report and confusion matrix.

## Dependencies

See `requirements.txt`. The scripts expect the existing file at `data/ml_ready/customer_ml_ready.csv` by default. If your project layout differs, pass its path with `--data`.
