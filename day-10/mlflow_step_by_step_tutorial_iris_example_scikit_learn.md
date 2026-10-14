# MLflow Step-by-step Tutorial — Iris (scikit-learn)

**Goal:** Walk through installing MLflow, running a local tracking UI/server, tracking experiments for a scikit-learn model trained on the Iris dataset, registering the best model in the Model Registry, and serving that model locally.

---

## Table of contents

1. Overview & prerequisites
2. Install MLflow (recommended setups)
3. Local quickstart: `mlflow ui` and `mlruns`
4. Example project: `train_iris_mlflow.py` (code + explanation)
5. Run the experiment and explore the UI
6. Using a local MLflow Tracking Server (sqlite backend + artifact root)
7. Model Registry: register, transition stages, and programmatic control
8. Serve the registered model locally and query it
9. Tips, best practices, and troubleshooting
10. Appendix: full code files
11. **Bonus Example: Simple Python Function with MLflow Logging**

---

## 1) Overview & prerequisites

What MLflow gives you for a typical ML project:

- Experiment and run tracking (parameters, metrics, artifacts).
- A web UI to compare runs and examine artifacts.
- A Model Registry to version and stage models (Staging / Production).
- Tools to package and serve models (MLflow Models).

Prerequisites:

- Python 3.8+ (adjust if your environment differs)
- `pip` and optionally `conda` (MLflow Projects feature can use conda)
- Basic tooling: `git`, `virtualenv` or `venv` recommended


## 2) Install MLflow

Create and activate a virtual environment (recommended):

```bash
python -m venv .venv
source .venv/bin/activate    # macOS / Linux
.venv\Scripts\activate      # Windows (PowerShell: .venv\Scripts\Activate.ps1)
```

Install MLflow and scikit-learn:

```bash
pip install mlflow[extras] scikit-learn pandas matplotlib joblib
```

> Notes:
> - `mlflow[extras]` installs optional dependencies that enable additional MLflow features (scikit-learn flavors, serving integrations, etc.). If you need a lighter install, `pip install mlflow` or `pip install mlflow-skinny` are alternatives.


## 3) Local quickstart: `mlflow ui` and `mlruns`

A minimal local flow for a solo developer:

1. Run your training script that calls `mlflow` APIs. By default, MLflow writes tracking data into a local `./mlruns` directory.
2. Start the MLflow UI to view the runs:

```bash
mlflow ui --port 5000
```

Then open `http://localhost:5000` in your browser to inspect experiments and runs.


## 4) Example project: `train_iris_mlflow.py`

Create a folder `mlflow-iris-demo/` and inside that create `train_iris_mlflow.py`.

**Purpose:** train a `RandomForestClassifier` on the Iris dataset, log params/metrics/artifacts, and save the model using `mlflow.sklearn.log_model()`.

```python
# train_iris_mlflow.py
import os
import mlflow
import mlflow.sklearn
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import pandas as pd
import joblib
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

# Optional: set an experiment name (creates it if not exists)
mlflow.set_experiment("Iris-Experiment")

def train_and_log(n_estimators=100, max_depth=None):
    iris = load_iris(as_frame=True)
    X = iris.data
    y = iris.target
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    params = {"n_estimators": n_estimators, "max_depth": max_depth}

    with mlflow.start_run() as run:
        clf = RandomForestClassifier(**{k: v for k, v in params.items() if v is not None}, random_state=42)
        clf.fit(X_train, y_train)

        preds = clf.predict(X_test)
        acc = accuracy_score(y_test, preds)

        # Log params and metrics
        mlflow.log_params(params)
        mlflow.log_metric("accuracy", acc)

        # Log sklearn model (MLflow stores model artifacts and flavor metadata)
        mlflow.sklearn.log_model(clf, "model")

        # Save and log an artifact (confusion matrix image)
        cm = confusion_matrix(y_test, preds)
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=load_iris().target_names)
        disp.plot()
        cm_path = "confusion_matrix.png"
        plt.savefig(cm_path)
        plt.close()
        mlflow.log_artifact(cm_path)

        print("Run ID:", run.info.run_id)

if __name__ == "__main__":
    train_and_log(n_estimators=100, max_depth=5)
```

**Notes about the code:**

- `mlflow.set_experiment` organizes runs under a named experiment.
- Within `mlflow.start_run()` we log parameters, metrics, artifacts and then the model with `mlflow.sklearn.log_model()`.
- The model and artifacts are stored under `./mlruns` by default (or under your configured backend/artifact store).


## 5) Run the experiment and explore the UI

1. Run the training script:

```bash
python train_iris_mlflow.py
```

2. Start the MLflow UI (if not yet started):

```bash
mlflow ui --port 5000
```

3. Open `http://localhost:5000` and click the `Iris-Experiment`. You should see your run(s) listed with params, metrics, and artifacts.

4. Use the UI's run comparison to compare multiple runs side-by-side.


## 6) Using a local MLflow Tracking Server (sqlite) — a step toward teamwork

For multi-user or centralized tracking, start a Tracking Server with a persistent SQL backend and a dedicated artifact root.

**Example (sqlite + local file artifact store):**

```bash
mkdir -p mlflow-data
mlflow server \
  --backend-store-uri sqlite:///$(pwd)/mlflow-data/mlflow.db \
  --default-artifact-root $(pwd)/mlflow-data/artifacts \
  --host 0.0.0.0 --port 5000
```

Notes:
- `--backend-store-uri` is where MLflow stores run metadata (SQL DB). Use PostgreSQL / MySQL in production.
- `--default-artifact-root` is the base location for artifacts (models, images). In production you normally point this to S3 / GCS / Azure Blob.
- If you want the tracking server to *serve* artifacts itself, there are additional flags (`--serve-artifacts` / `--artifacts-destination`).

To point your training code to the remote server, set the tracking URI before creating runs:

```python
import mlflow
mlflow.set_tracking_uri("http://your-server-host:5000")
mlflow.set_experiment("Iris-Experiment")
# then proceed with mlflow.start_run() as before
```


## 7) Model Registry: register and manage model versions

After logging a model to a run, register it in the Model Registry either via the UI or programmatically.

**Programmatic example** (register a model and transition to Staging):

```python
from mlflow.tracking import MlflowClient
import mlflow

client = MlflowClient(tracking_uri="http://your-server-host:5000")
run_id = "<PASTE_RUN_ID_FROM_TRAINING>"
model_uri = f"runs:/{run_id}/model"
# Register
result = mlflow.register_model(model_uri, "IrisRF")
print(result.name, result.version)

# Transition stage (e.g., to Staging)
client.transition_model_version_stage(name="IrisRF", version=result.version, stage="Staging")
```

You can also do this in the MLflow UI by selecting a logged model and clicking **Register model**.


## 8) Serve the registered model locally and call it

Serve a registered model (or a model from a run) locally using MLflow's built-in model server.

**Serve a registered model version:**

```bash
mlflow models serve -m "models:/IrisRF/1" --no-conda -p 1234
```

**Call the model with `curl`:**

```bash
curl -X POST -H "Content-Type:application/json" \
  -d '{"columns": ["sepal length (cm)", "sepal width (cm)", "petal length (cm)", "petal width (cm)"], "data": [[5.1,3.5,1.4,0.2]]}' \
  http://127.0.0.1:1234/invocations
```

The server will return a JSON array of predictions.


## 9) Tips, best practices, and troubleshooting

- **Experiment names**: use `mlflow.set_experiment("proj-name/exp-name")` for hierarchy.
- **Reproducibility**: log environment information (`mlflow.log_param("python_version", sys.version)`) and use `conda.yaml` / `mlflow.projects` when needed.
- **Artifact storage**: for teams use S3/GCS/Azure Blob as artifact stores and a shared SQL DB (Postgres) for metadata.
- **Security**: when exposing a tracking server, secure it (TLS, auth) and use a production DB.
- **Port conflicts**: `mlflow ui` defaults to port 5000. Use `--port` to change.
- **Common errors**: if a model flavor fails to load on serve, check that the same dependency set (e.g., scikit-learn version) is available.


## 10) Appendix: Full files

- `train_iris_mlflow.py` (already shown in Section 4)
- Optionally: `register_and_transition.py` (for programmatic registry operations)
- `requirements.txt` suggestion:

```
mlflow[extras]
scikit-learn
pandas
matplotlib
joblib
```


## 11) Bonus Example: Simple Python Function with MLflow Logging

Sometimes you want to demonstrate MLflow basics without training an ML model. Here’s a simple script that logs parameters, metrics, tags, and artifacts using a mathematical function.

Create a file `simple_math_mlflow.py`:

```python
import mlflow
import math
import matplotlib.pyplot as plt

mlflow.set_experiment("Simple-Math")

with mlflow.start_run() as run:
    # Example parameters
    base = 2
    exponent = 5
    mlflow.log_param("base", base)
    mlflow.log_param("exponent", exponent)

    # Compute a result and log as a metric
    result = math.pow(base, exponent)
    mlflow.log_metric("power_result", result)

    # Add a custom tag
    mlflow.set_tag("demo_type", "math_function")

    # Generate a simple plot artifact
    x = list(range(1, 11))
    y = [math.pow(base, i) for i in x]
    plt.plot(x, y, marker="o")
    plt.title(f"{base}^x growth")
    plt.xlabel("x")
    plt.ylabel("y")
    plot_path = "power_plot.png"
    plt.savefig(plot_path)
    plt.close()
    mlflow.log_artifact(plot_path)

    print("Run ID:", run.info.run_id)
```

**What this demonstrates:**
- Logging parameters (`base`, `exponent`)
- Logging a metric (`power_result`)
- Adding tags (`demo_type`)
- Logging a plot as an artifact

Run it with:

```bash
python simple_math_mlflow.py
```

Check the MLflow UI — you’ll see a run under `Simple-Math` with params, metrics, tags, and an artifact plot.

---

*End of tutorial document.*

