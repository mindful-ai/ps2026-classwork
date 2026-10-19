"""FastAPI inference service that loads the latest trained models from MLflow."""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from threading import RLock
from typing import Any

import mlflow
import mlflow.sklearn
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("mlflow-fastapi")

MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
MLFLOW_EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME", "data-engineering-with-astro-customer-ml"
)

# These run names match the training scripts supplied with this project.
MODEL_CONFIG = {
    "segmentation": {
        "run_name": "customer-segmentation-kmeans",
        "description": "KMeans customer segmentation",
    },
    "spending": {
        "run_name": "customer-spending-random-forest",
        "description": "Historical aggregate customer-spend estimation",
    },
    "churn": {
        "run_name": "customer-churn-proxy-random-forest",
        "description": "Heuristic churn-proxy classifier (not observed churn)",
    },
}

app = FastAPI(
    title="Customer MLflow Inference API",
    version="1.0.0",
    description=(
        "Serves customer segmentation, spending estimation, and churn-proxy models "
        "loaded from the configured MLflow Tracking Server."
    ),
)

client: mlflow.tracking.MlflowClient | None = None
experiment_id: str | None = None
models: dict[str, dict[str, Any]] = {}
model_lock = RLock()


class PredictionRequest(BaseModel):
    # Each record must contain the numeric feature columns used by the selected model.
    records: list[dict[str, float]] = Field(
        ..., min_length=1, description="One or more feature records."
    )


def _configure_mlflow() -> None:
    global client, experiment_id
    mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
    client = mlflow.tracking.MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)
    experiment = client.get_experiment_by_name(MLFLOW_EXPERIMENT_NAME)
    if experiment is None:
        experiment_id = None
        logger.warning("MLflow experiment not found: %s", MLFLOW_EXPERIMENT_NAME)
    else:
        experiment_id = experiment.experiment_id


def _load_one_model(key: str) -> dict[str, Any]:
    if client is None or experiment_id is None:
        raise RuntimeError(
            f"MLflow experiment '{MLFLOW_EXPERIMENT_NAME}' was not found at "
            f"{MLFLOW_TRACKING_URI}. Train the models first."
        )

    run_name = MODEL_CONFIG[key]["run_name"]
    runs = client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=f"attributes.run_name = '{run_name}' and attributes.status = 'FINISHED'",
        order_by=["attribute.start_time DESC"],
        max_results=1,
    )
    if not runs:
        raise RuntimeError(
            f"No FINISHED MLflow run named '{run_name}' was found. "
            "Run the corresponding training script first."
        )

    run = runs[0]
    run_id = run.info.run_id
    model_uri = f"runs:/{run_id}/model"
    model = mlflow.sklearn.load_model(model_uri)

    # Training scripts store the exact model feature order in this artifact.
    local_metadata = client.download_artifacts(run_id, "metadata/feature_columns.json")
    feature_columns = json.loads(Path(local_metadata).read_text(encoding="utf-8"))
    if not feature_columns:
        raise RuntimeError(f"Empty feature list in MLflow run {run_id}")

    return {
        "key": key,
        "description": MODEL_CONFIG[key]["description"],
        "run_name": run_name,
        "run_id": run_id,
        "model_uri": model_uri,
        "model": model,
        "features": feature_columns,
        "loaded": True,
        "error": None,
    }


def reload_models() -> dict[str, Any]:
    """Reload latest finished run for each model without stopping the API."""
    results: dict[str, Any] = {}
    with model_lock:
        for key in MODEL_CONFIG:
            try:
                loaded = _load_one_model(key)
                models[key] = loaded
                results[key] = {
                    "loaded": True,
                    "run_id": loaded["run_id"],
                    "features": loaded["features"],
                }
                logger.info("Loaded %s from MLflow run %s", key, loaded["run_id"])
            except Exception as exc:
                logger.exception("Could not load model '%s'", key)
                # Retain a previously loaded model if a refresh attempt fails.
                if key not in models:
                    models[key] = {
                        "key": key,
                        "description": MODEL_CONFIG[key]["description"],
                        "loaded": False,
                        "error": str(exc),
                    }
                results[key] = {
                    "loaded": bool(models[key].get("loaded")),
                    "error": str(exc),
                }
    return results


@app.on_event("startup")
def startup_event() -> None:
    try:
        _configure_mlflow()
        reload_models()
    except Exception:
        # Keep the API available so /health and /models can explain the problem.
        logger.exception("Initial MLflow setup failed")


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "Customer MLflow Inference API",
        "docs": "/docs",
        "health": "/health",
        "models": "/models",
    }


@app.get("/health")
def health() -> dict[str, Any]:
    loaded = [key for key, value in models.items() if value.get("loaded")]
    return {
        "status": "ok" if loaded else "degraded",
        "mlflow_tracking_uri": MLFLOW_TRACKING_URI,
        "experiment_name": MLFLOW_EXPERIMENT_NAME,
        "loaded_models": loaded,
        "expected_models": list(MODEL_CONFIG),
    }


@app.get("/models")
def list_models() -> dict[str, Any]:
    response: dict[str, Any] = {}
    for key, config in MODEL_CONFIG.items():
        item = models.get(key, {})
        response[key] = {
            "description": config["description"],
            "loaded": bool(item.get("loaded")),
            "run_name": item.get("run_name", config["run_name"]),
            "run_id": item.get("run_id"),
            "model_uri": item.get("model_uri"),
            "features": item.get("features", []),
            "error": item.get("error"),
        }
    return response


@app.post("/reload-models")
def reload_models_endpoint() -> dict[str, Any]:
    """Reload latest FINISHED MLflow runs after training a new model version."""
    try:
        _configure_mlflow()
        results = reload_models()
        return {"message": "Model reload attempted", "results": results}
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Could not connect to MLflow: {exc}") from exc


def _predict(model_key: str, payload: PredictionRequest) -> dict[str, Any]:
    with model_lock:
        model_info = models.get(model_key)
        if not model_info or not model_info.get("loaded"):
            detail = (model_info or {}).get("error", "Model is not loaded.")
            raise HTTPException(
                status_code=503,
                detail=f"Model '{model_key}' is unavailable. {detail}",
            )
        model = model_info["model"]
        features = model_info["features"]
        run_id = model_info["run_id"]

    records = payload.records
    expected = set(features)
    prepared: list[dict[str, float]] = []
    for index, record in enumerate(records):
        missing = sorted(expected - set(record))
        extra = sorted(set(record) - expected)
        if missing or extra:
            raise HTTPException(
                status_code=422,
                detail={
                    "record_index": index,
                    "missing_features": missing,
                    "unexpected_features": extra,
                    "expected_features": features,
                },
            )
        prepared.append({name: record[name] for name in features})

    frame = pd.DataFrame(prepared, columns=features)
    try:
        predictions = model.predict(frame)
        result: dict[str, Any] = {
            "model": model_key,
            "run_id": run_id,
            "count": len(records),
            "predictions": [],
        }
        if model_key == "segmentation":
            result["predictions"] = [
                {"cluster": int(value)} for value in predictions
            ]
        elif model_key == "spending":
            result["predictions"] = [
                {"estimated_total_spend": float(value)} for value in predictions
            ]
        elif model_key == "churn":
            probabilities = model.predict_proba(frame)[:, 1]
            result["predictions"] = [
                {
                    "churn_proxy_prediction": int(label),
                    "churn_proxy_probability": float(probability),
                    "label_note": "Heuristic proxy only; not a validated churn prediction.",
                }
                for label, probability in zip(predictions, probabilities)
            ]
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Prediction failed for model '%s'", model_key)
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}") from exc


@app.post("/predict/segmentation")
def predict_segmentation(payload: PredictionRequest) -> dict[str, Any]:
    """Return a KMeans cluster assignment for each supplied customer."""
    return _predict("segmentation", payload)


@app.post("/predict/spending")
def predict_spending(payload: PredictionRequest) -> dict[str, Any]:
    """Estimate historical aggregate spend; this is not a future-period forecast."""
    return _predict("spending", payload)


@app.post("/predict/churn")
def predict_churn_proxy(payload: PredictionRequest) -> dict[str, Any]:
    """Return the demo recency-based churn proxy, not observed churn."""
    return _predict("churn", payload)


@app.post("/predict/{model_name}")
def predict_by_name(model_name: str, payload: PredictionRequest) -> dict[str, Any]:
    """Generic endpoint: model_name is segmentation, spending, or churn."""
    if model_name not in MODEL_CONFIG:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown model '{model_name}'. Choose one of {list(MODEL_CONFIG)}.",
        )
    return _predict(model_name, payload)
