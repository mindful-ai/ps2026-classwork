"""Train a customer segmentation model and log the run to MLflow."""
from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from common import (
    DEFAULT_EXPERIMENT_NAME,
    DEFAULT_TRACKING_URI,
    configure_mlflow,
    load_data,
    log_dataset,
    log_model,
    log_feature_columns,
    numeric_features,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--data",
        default=str(Path(__file__).resolve().parents[1] / "data" / "ml_ready" / "customer_ml_ready.csv"),
        help="Path to customer_ml_ready.csv",
    )
    parser.add_argument("--tracking-uri", default=DEFAULT_TRACKING_URI)
    parser.add_argument("--experiment-name", default=DEFAULT_EXPERIMENT_NAME)
    parser.add_argument("--clusters", type=int, default=4)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    df, data_path = load_data(args.data)
    X = numeric_features(df)
    if args.clusters < 2 or args.clusters >= len(X):
        raise ValueError("--clusters must be >= 2 and less than the number of rows.")

    configure_mlflow(args.tracking_uri, args.experiment_name)
    model = Pipeline(
        steps=[
            ("scaler", StandardScaler()),
            ("kmeans", KMeans(
                n_clusters=args.clusters,
                random_state=args.random_state,
                n_init=10,
            )),
        ]
    )

    with mlflow.start_run(run_name="customer-segmentation-kmeans"):
        log_dataset(df, data_path)
        log_feature_columns(X.columns)
        mlflow.log_params({
            "model_type": "KMeans",
            "n_clusters": args.clusters,
            "random_state": args.random_state,
            "scaling": "StandardScaler",
            "feature_count": X.shape[1],
        })
        model.fit(X)
        labels = model.predict(X)
        mlflow.log_metric("inertia", float(model.named_steps["kmeans"].inertia_))
        if len(set(labels)) > 1 and len(set(labels)) < len(labels):
            mlflow.log_metric("silhouette_score", float(silhouette_score(
                model.named_steps["scaler"].transform(X),
                labels,
                sample_size=min(2000, len(X)),
                random_state=args.random_state,
            )))

        assignments = pd.DataFrame({
            "customer_id": df["customer_id"],
            "cluster": labels,
        })
        assignments.to_csv("customer_cluster_assignments.csv", index=False)
        mlflow.log_artifact("customer_cluster_assignments.csv")

        profile = X.assign(cluster=labels).groupby("cluster").mean(numeric_only=True)
        profile.to_csv("customer_cluster_profile.csv")
        mlflow.log_artifact("customer_cluster_profile.csv")
        log_model(model, X)
        print(f"Logged customer segmentation run to {args.tracking_uri}")


if __name__ == "__main__":
    main()
