import hashlib
import os
import subprocess
from pathlib import Path

import mlflow
import mlflow.sklearn
import pandas as pd
from mlflow.models import infer_signature
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split

from src.validate import validate_data

DATA_PATH = "data/customers.csv"
TARGET = "churn"


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def get_git_commit():
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "unknown"


def main():
    df = pd.read_csv(DATA_PATH)
    validate_data(df)

    X = df.drop(columns=[TARGET])
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    C = float(os.getenv("MODEL_C", "1.0"))
    model = LogisticRegression(C=C, max_iter=1000)

    mlflow.set_experiment("customer-churn")

    with mlflow.start_run() as run:
        model.fit(X_train, y_train)
        predictions = model.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision": precision_score(y_test, predictions, zero_division=0),
            "recall": recall_score(y_test, predictions, zero_division=0),
            "f1": f1_score(y_test, predictions, zero_division=0),
        }

        mlflow.log_params({
            "model_type": "LogisticRegression",
            "C": C,
            "max_iter": 1000,
            "test_size": 0.2,
            "random_state": 42,
            "dataset_sha256": sha256_file(DATA_PATH),
            "git_commit": get_git_commit(),
        })
        mlflow.log_metrics(metrics)

        signature = infer_signature(X_test, model.predict(X_test))
        mlflow.sklearn.log_model(
            sk_model=model,
            name="churn_model",
            signature=signature,
            input_example=X_test.head(3),
        )

        report_dir = Path("artifacts")
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"metrics-{run.info.run_id}.csv"
        pd.DataFrame([metrics]).to_csv(report_path, index=False)
        mlflow.log_artifact(str(report_path))

        print("Run ID:", run.info.run_id)
        print("Metrics:", metrics)
        print("Model URI:", f"runs:/{run.info.run_id}/churn_model")


if __name__ == "__main__":
    main()
