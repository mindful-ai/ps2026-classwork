"""Train a customer-spend regression model and log it to MLflow."""
from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

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
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=300)
    args = parser.parse_args()

    df, data_path = load_data(args.data)
    if "total_spend" not in df.columns:
        raise ValueError("Target column 'total_spend' was not found.")
    # Exclude target and average_order_value because it is directly derived from spend.
    X = numeric_features(df, exclude={"total_spend", "average_order_value"})
    y = pd.to_numeric(df["total_spend"], errors="raise")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state
    )
    configure_mlflow(args.tracking_uri, args.experiment_name)
    model = RandomForestRegressor(
        n_estimators=args.n_estimators,
        random_state=args.random_state,
        n_jobs=-1,
    )

    with mlflow.start_run(run_name="customer-spending-random-forest"):
        log_dataset(df, data_path)
        log_feature_columns(X.columns)
        mlflow.log_params({
            "model_type": "RandomForestRegressor",
            "target": "total_spend",
            "n_estimators": args.n_estimators,
            "test_size": args.test_size,
            "random_state": args.random_state,
            "feature_count": X.shape[1],
            "target_note": "Historical aggregate spend estimation; not a future-period forecast.",
        })
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        mlflow.log_metrics({
            "mae": float(mean_absolute_error(y_test, predictions)),
            "rmse": float(mean_squared_error(y_test, predictions) ** 0.5),
            "r2": float(r2_score(y_test, predictions)),
        })

        importance = pd.DataFrame({
            "feature": X.columns,
            "importance": model.feature_importances_,
        }).sort_values("importance", ascending=False)
        importance.to_csv("spending_feature_importance.csv", index=False)
        mlflow.log_artifact("spending_feature_importance.csv")
        log_model(model, X_test)
        print(f"Logged spending regression run to {args.tracking_uri}")


if __name__ == "__main__":
    main()
