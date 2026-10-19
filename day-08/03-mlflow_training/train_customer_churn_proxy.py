"""Train a churn-proxy classifier and log the run to MLflow."""
from __future__ import annotations

import argparse
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
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
    parser.add_argument("--recency-threshold-days", type=int, default=90)
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    parser.add_argument("--n-estimators", type=int, default=300)
    args = parser.parse_args()

    df, data_path = load_data(args.data)
    if "recency_days" not in df.columns:
        raise ValueError("Column 'recency_days' is required to create the demo proxy target.")
    if args.recency_threshold_days < 1:
        raise ValueError("--recency-threshold-days must be positive.")

    # There is no true churn label in this dataset. This is an explicitly labelled
    # demonstration proxy; recency_days is excluded from features to avoid direct leakage.
    y = (pd.to_numeric(df["recency_days"], errors="raise") >= args.recency_threshold_days).astype(int)
    X = numeric_features(df, exclude={"recency_days"})
    if y.nunique() != 2:
        raise ValueError(
            "Proxy target has only one class. Change --recency-threshold-days."
        )

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=args.random_state, stratify=y
    )
    configure_mlflow(args.tracking_uri, args.experiment_name)
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        random_state=args.random_state,
        class_weight="balanced",
        n_jobs=-1,
    )

    with mlflow.start_run(run_name="customer-churn-proxy-random-forest"):
        log_dataset(df, data_path)
        log_feature_columns(X.columns)
        mlflow.log_params({
            "model_type": "RandomForestClassifier",
            "target": "churn_proxy",
            "target_definition": f"recency_days >= {args.recency_threshold_days}",
            "recency_threshold_days": args.recency_threshold_days,
            "n_estimators": args.n_estimators,
            "test_size": args.test_size,
            "random_state": args.random_state,
            "class_weight": "balanced",
            "feature_count": X.shape[1],
            "label_warning": "Proxy label only; dataset contains no observed churn outcome.",
        })
        mlflow.set_tag("label.type", "heuristic_proxy_not_observed_churn")
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)
        probabilities = model.predict_proba(X_test)[:, 1]
        metrics = {
            "accuracy": float(accuracy_score(y_test, predictions)),
            "precision": float(precision_score(y_test, predictions, zero_division=0)),
            "recall": float(recall_score(y_test, predictions, zero_division=0)),
            "f1": float(f1_score(y_test, predictions, zero_division=0)),
            "positive_label_rate": float(y.mean()),
        }
        if y_test.nunique() == 2:
            metrics["roc_auc"] = float(roc_auc_score(y_test, probabilities))
        mlflow.log_metrics(metrics)

        report = classification_report(y_test, predictions, zero_division=0)
        Path("churn_proxy_classification_report.txt").write_text(report, encoding="utf-8")
        mlflow.log_artifact("churn_proxy_classification_report.txt")
        cm = pd.DataFrame(
            confusion_matrix(y_test, predictions),
            index=["actual_0", "actual_1"],
            columns=["predicted_0", "predicted_1"],
        )
        cm.to_csv("churn_proxy_confusion_matrix.csv")
        mlflow.log_artifact("churn_proxy_confusion_matrix.csv")
        log_model(model, X_test)
        print(f"Logged churn-proxy classification run to {args.tracking_uri}")


if __name__ == "__main__":
    main()
