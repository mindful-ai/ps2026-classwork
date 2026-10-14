# MLflow Multi-Run Iris Classification

A practical MLflow 3.x project demonstrating multiple training runs, experiment tracking, model comparison, model registration, and inference using a registered model alias.

## 1. Project structure

```text
mlflow-multi/
├── train.py
├── predict.py
└── mlflow.db             # Created by MLflow's SQLite backend
```

The MLflow tracking server stores run metadata and model-registry metadata in SQLite. Model files and other artifacts are stored through the tracking server's configured artifact store.

## 2. Prerequisites

Activate your Python virtual environment and install the dependencies:

```bash
pip install mlflow scikit-learn matplotlib pandas
```

This example uses the MLflow tracking server at `http://localhost:5000`.

## 3. Start the MLflow server

From the project directory, run this command in Terminal 1:

```bash
mlflow server --backend-store-uri sqlite:///mlflow.db --host 127.0.0.1 --port 5000
```

Keep the terminal running. Open the UI at [http://localhost:5000](http://localhost:5000).

> Run the server and training script from the same project directory so the relative SQLite URI resolves to the same database file.

## 4. `train.py` — multiple runs and registration

This script trains three Logistic Regression models using different values of `C`, logs parameters and metrics, records a confusion-matrix artifact, compares runs by macro F1, registers the best matching model, and assigns it the `champion` alias.

```python
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
```

### Why use a batch ID?

The script adds a unique `training_batch_id` tag to each run and filters on that tag during model selection. This prevents runs from earlier executions from accidentally being selected as the winner of the current batch.

## 5. Run the training script

In Terminal 2, from the same project directory and virtual environment:

```bash
python train.py
```

The script will:

1. Train three candidate models.
2. Log parameters and evaluation metrics.
3. Save a confusion matrix for each run.
4. Log each trained model.
5. Select the run with the highest macro F1 score in the current batch.
6. Register that model as a version of `IrisClassifier`.
7. Set the `champion` alias to that version.

The exact scores and version number depend on the run and the existing model registry.

## 6. `predict.py` — use the registered model

Create `predict.py`:

```python
import mlflow
import mlflow.sklearn
import pandas as pd

mlflow.set_tracking_uri("http://localhost:5000")

model_uri = "models:/IrisClassifier@champion"
model = mlflow.sklearn.load_model(model_uri)

sample = pd.DataFrame(
    [[5.1, 3.5, 1.4, 0.2]],
    columns=[
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
    ],
)

prediction = int(model.predict(sample)[0])
species = ["setosa", "versicolor", "virginica"][prediction]

print("Predicted class:", prediction)
print("Predicted species:", species)
```

Run it:

```bash
python predict.py
```

The model is loaded through the `champion` alias, so prediction code does not need to hard-code a specific model version.

## 7. Explore the results in the MLflow UI

Open [http://localhost:5000](http://localhost:5000).

Under the **Iris Classification** experiment, inspect each run's:

- Parameters: `C`, `max_iter`, `solver`, and `random_state`
- Metrics: accuracy, macro precision, macro recall, and macro F1
- Tags: dataset, model type, and training batch ID
- Artifacts: `confusion_matrix.png` and the logged model

Open the **Models** or model-registry view and select `IrisClassifier` to inspect its versions and `champion` alias. The exact navigation may vary by MLflow UI version.

## 8. Key concepts demonstrated

| Concept | What it demonstrates |
|---|---|
| Experiment tracking | Organizes related training runs |
| Parameters | Records model configuration |
| Metrics | Quantifies model performance |
| Artifacts | Stores diagnostic plots and other files |
| Model comparison | Selects a candidate using macro F1 |
| Model Registry | Maintains versioned registered models |
| Alias | Points `champion` to a chosen model version |
| Inference | Loads and uses the registered model independently |

## 9. Practical considerations

- **Choose the metric deliberately.** Macro F1 gives equal weight to each class. The best metric depends on the application and business cost of errors.
- **Use a separate validation set for model selection.** This example uses one held-out test set for a compact demonstration. In a production workflow, tune hyperparameters on training/validation data and reserve the test set for final evaluation.
- **Add acceptance thresholds.** A production pipeline should register or promote a model only if it meets explicit quality and safety criteria.
- **Manage dependencies.** Use a pinned requirements file or an environment managed by your deployment pipeline.
- **Keep server and client configuration consistent.** Both scripts use `http://localhost:5000`. If running in containers or on another machine, configure a reachable server address.
- **Back up the tracking database and artifact store.** The database contains run and registry metadata; model artifacts are stored separately according to server configuration.
- **Avoid concurrent alias updates without a promotion policy.** In a production system, define how a candidate is evaluated and who or what is allowed to update the `champion` alias.

## 10. Workflow summary

```text
Load Iris data
      |
      v
Train multiple Logistic Regression configurations
      |
      v
Log parameters, metrics, plots, and model artifacts
      |
      v
Compare runs by macro F1 within the current batch
      |
      v
Register the selected model version
      |
      v
Assign the champion alias
      |
      v
Load models:/IrisClassifier@champion
      |
      v
Predict on new input
```
