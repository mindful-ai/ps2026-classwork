# FastAPI + MLflow Customer Model Serving

This service loads the **latest FINISHED runs** for three models from the MLflow Tracking Server. It does not train models inside FastAPI.

## Models and endpoints

| Endpoint | Purpose |
|---|---|
| `GET /` | Service entry point |
| `GET /health` | API and model-load status |
| `GET /models` | Loaded model names, MLflow run IDs, and required features |
| `POST /predict/segmentation` | KMeans customer cluster |
| `POST /predict/spending` | Historical aggregate spend estimate |
| `POST /predict/churn` | Heuristic churn-proxy prediction |
| `POST /predict/{model_name}` | Generic prediction route for `segmentation`, `spending`, or `churn` |
| `POST /reload-models` | Reload latest finished MLflow runs after retraining |

The run names must match the training scripts:
- `customer-segmentation-kmeans`
- `customer-spending-random-forest`
- `customer-churn-proxy-random-forest`

The model artifact must be logged at `model`, and feature metadata at `metadata/feature_columns.json`. The supplied training scripts already do this.

## 1. Start MLflow

From the project environment, start the tracking server using the same backend and artifact configuration used during training. Example:

```powershell
mlflow server --host 127.0.0.1 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts
```

Open `http://127.0.0.1:5000` and confirm that the `data-engineering-with-astro-customer-ml` experiment contains successful runs for all three training scripts.

## 2. Train the models

Run the three training scripts from the project environment before starting inference:

```powershell
python mlflow_training/train_customer_segmentation.py
python mlflow_training/train_customer_spending.py
python mlflow_training/train_customer_churn_proxy.py
```

If your files are in a different folder, adjust the paths. Use the same MLflow tracking URI and experiment name for training and serving.

## 3. Install and run FastAPI

Create/activate your virtual environment, then from the directory containing `app.py`:

```powershell
pip install -r requirements.txt
$env:MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
$env:MLFLOW_EXPERIMENT_NAME = "data-engineering-with-astro-customer-ml"
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open Swagger UI at `http://127.0.0.1:8000/docs`.

If the models are not available at startup, the API remains running and `/models` reports the loading error. Train the models, then call `POST /reload-models`.

## 4. Inspect health and model metadata

```powershell
curl.exe http://127.0.0.1:8000/health
curl.exe http://127.0.0.1:8000/models
```

Use the `features` array returned by `/models` as the source of truth for request payloads. The API validates that each record has exactly the required numeric feature names.

## 5. Send a prediction

Example request shape (replace the placeholder feature names and values with the exact feature list returned by `/models`):

```json
{
  "records": [
    {
      "REPLACE_WITH_FEATURE_NAME_FROM_MODELS": 1.0
    }
  ]
}
```

Example PowerShell request template:

```powershell
$body = @{
  records = @(
    @{
      REPLACE_WITH_FEATURE_NAME_FROM_MODELS = 1.0
    }
  )
} | ConvertTo-Json -Depth 5

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/predict/segmentation" `
  -ContentType "application/json" `
  -Body $body
```

That template intentionally uses a placeholder: use all feature names returned for the chosen model. Do not send `customer_id` unless `/models` lists it.

## 6. Reload after retraining

After a new successful training run, call:

```powershell
curl.exe -X POST http://127.0.0.1:8000/reload-models
```

The service selects the most recent finished run with the expected run name for each model. A failed refresh does not discard an already-loaded model.

## Important notes

- **MLflow is the model source:** models are loaded from `runs:/<run_id>/model`; the API does not use local model files.
- The serving process must be able to reach the tracking server and its artifact store. If MLflow uses remote artifact storage, configure credentials and permissions in the API process.
- The three models were trained with different feature exclusions. Always use the feature list for the endpoint you call.
- Spending is a historical aggregate estimate, not a forecast of future spending.
- The churn model uses a heuristic label based on `recency_days >= threshold`; it is a teaching/demo proxy, not a validated churn outcome.
- For production, add authentication, request-size limits, structured access logs, monitoring, and deployment-specific secrets management before exposing the service publicly.
