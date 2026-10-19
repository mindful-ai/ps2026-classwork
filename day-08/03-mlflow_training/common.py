"""Shared MLflow setup for independently launched customer-model training scripts."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import mlflow
import pandas as pd

DEFAULT_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://127.0.0.1:5000")
DEFAULT_EXPERIMENT_NAME = os.getenv(
    "MLFLOW_EXPERIMENT_NAME", "data-engineering-with-astro-customer-ml"
)


def load_data(path: str | Path) -> tuple[pd.DataFrame, Path]:
    data_path = Path(path).expanduser().resolve()
    if not data_path.exists():
        raise FileNotFoundError(
            f"ML-ready dataset not found: {data_path}\n"
            "Pass the correct file using --data."
        )

    df = pd.read_csv(data_path)
    if df.empty:
        raise ValueError(f"Dataset is empty: {data_path}")
    if "customer_id" not in df.columns:
        raise ValueError("Expected 'customer_id' column was not found.")
    if df["customer_id"].isna().any():
        raise ValueError("'customer_id' contains missing values.")
    return df, data_path


def configure_mlflow(tracking_uri: str, experiment_name: str) -> None:
    """Point every training script at the same configured tracking server."""
    mlflow.set_tracking_uri(tracking_uri)
    mlflow.set_experiment(experiment_name)


def log_dataset(df: pd.DataFrame, data_path: Path) -> None:
    """Log dataset lineage and a content hash for reproducibility."""
    sha256 = hashlib.sha256(data_path.read_bytes()).hexdigest()
    mlflow.set_tag("project", "data-engineering-with-astro")
    mlflow.set_tag("dataset.name", data_path.name)
    mlflow.set_tag("dataset.path", str(data_path))
    mlflow.set_tag("dataset.sha256", sha256)

    dataset = mlflow.data.from_pandas(
        df,
        source=str(data_path),
        name="customer_ml_ready",
    )
    mlflow.log_input(dataset, context="training")
    # Store a copy of the exact input CSV with this run, in addition to dataset lineage.
    mlflow.log_artifact(str(data_path), artifact_path="input_data")
    mlflow.log_param("dataset_rows", int(df.shape[0]))
    mlflow.log_param("dataset_columns", int(df.shape[1]))



def log_feature_columns(columns) -> None:
    """Store the complete feature list as an artifact, not a long MLflow parameter."""
    feature_path = Path("feature_columns.json")
    feature_path.write_text(json.dumps(list(columns), indent=2), encoding="utf-8")
    mlflow.log_artifact(str(feature_path), artifact_path="metadata")

def log_model(model, X_example: pd.DataFrame, artifact_path: str = "model") -> None:
    """Log a scikit-learn model with an input signature and example."""
    from mlflow.models import infer_signature

    example = X_example.head(5).copy()
    predictions = model.predict(example)
    signature = infer_signature(example, predictions)
    mlflow.sklearn.log_model(
        sk_model=model,
        artifact_path=artifact_path,
        signature=signature,
        input_example=example,
    )


def numeric_features(
    df: pd.DataFrame,
    exclude: set[str] | None = None,
) -> pd.DataFrame:
    exclude = exclude or set()
    features = df.drop(
        columns=[col for col in ({"customer_id"} | exclude) if col in df.columns]
    )
    features = features.select_dtypes(include=["number"]).copy()
    if features.empty:
        raise ValueError("No numeric model features remain after exclusions.")
    if features.isna().any().any():
        raise ValueError("Numeric model features contain missing values.")
    return features
