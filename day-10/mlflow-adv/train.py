import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt

from mlflow import MlflowClient
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    ConfusionMatrixDisplay,
)

TRACKING_URI = "http://localhost:5000"
EXPERIMENT_NAME = "Iris Classification"
REGISTERED_MODEL_NAME = "IrisClassifier"

mlflow.set_tracking_uri(TRACKING_URI)
mlflow.set_experiment(EXPERIMENT_NAME)

client = MlflowClient(tracking_uri=TRACKING_URI)

print("Loading Iris dataset...", flush=True)

iris = load_iris(as_frame=True)
X = iris.data
y = iris.target

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y,
)

# A unique batch tag prevents older matching runs from being selected.
import uuid
batch_id = str(uuid.uuid4())
print(f"Training batch: {batch_id}", flush=True)

C_VALUES = [0.1, 1.0, 10.0]

for C in C_VALUES:
    params = {
        "C": C,
        "max_iter": 1000,
        "solver": "lbfgs",
        "random_state": 42,
    }

    run_name = f"logistic-regression-C-{C}"
    print(f"\nStarting run: {run_name}", flush=True)

    with mlflow.start_run(run_name=run_name) as run:
        mlflow.log_params(params)
        mlflow.set_tags({
            "model_type": "classification",
            "dataset": "Iris",
            "training_batch_id": batch_id,
        })

        model = LogisticRegression(**params)
        model.fit(X_train, y_train)

        predictions = model.predict(X_test)

        metrics = {
            "accuracy": accuracy_score(y_test, predictions),
            "precision_macro": precision_score(
                y_test, predictions, average="macro"
            ),
            "recall_macro": recall_score(
                y_test, predictions, average="macro"
            ),
            "f1_macro": f1_score(
                y_test, predictions, average="macro"
            ),
        }
        mlflow.log_metrics(metrics)

        fig, ax = plt.subplots(figsize=(5, 4))
        ConfusionMatrixDisplay.from_predictions(
            y_test,
            predictions,
            display_labels=iris.target_names,
            ax=ax,
        )
        fig.tight_layout()
        mlflow.log_figure(fig, "confusion_matrix.png")
        plt.close(fig)

        mlflow.sklearn.log_model(
            sk_model=model,
            name="iris_classifier",
            input_example=X_train.head(3),
        )

        print("Metrics:", metrics, flush=True)
        print("Run ID:", run.info.run_id, flush=True)

# Select only runs created by this execution.
experiment = client.get_experiment_by_name(EXPERIMENT_NAME)
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string=f"tags.training_batch_id = '{batch_id}'",
    order_by=["metrics.f1_macro DESC"],
    max_results=100,
)

if not runs:
    raise RuntimeError("No runs found for this training batch.")

best_run = runs[0]
best_f1 = best_run.data.metrics["f1_macro"]

print("\nBest run selected:")
print("Run ID:", best_run.info.run_id)
print("C:", best_run.data.params["C"])
print("Macro F1:", best_f1)

model_uri = f"runs:/{best_run.info.run_id}/iris_classifier"

print("\nRegistering best model...", flush=True)
registered_model = mlflow.register_model(
    model_uri=model_uri,
    name=REGISTERED_MODEL_NAME,
)

client.set_registered_model_alias(
    name=REGISTERED_MODEL_NAME,
    alias="champion",
    version=registered_model.version,
)

print("Registered model:", REGISTERED_MODEL_NAME)
print("Model version:", registered_model.version)
print("Champion alias assigned successfully.")
print("Training completed.")
