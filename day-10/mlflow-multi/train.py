import mlflow
import mlflow.sklearn
import matplotlib.pyplot as plt

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

print("MLflow version:", mlflow.__version__)
# 1. Configure experiment tracking
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("Iris Classification")

# 2. Load dataset
print("Loading Iris dataset...")
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

# 3. Define model parameters
print("Training Logistic Regression model...")
params = {
    "C": 1.0,
    "max_iter": 1000,
    "solver": "lbfgs",
    "random_state": 42,
}

# 4. Train and track one run
print("Starting MLflow run...")
with mlflow.start_run(run_name="logistic-regression-v1"):

    mlflow.log_params(params)
    mlflow.set_tag("model_type", "classification")
    mlflow.set_tag("dataset", "Iris")

    model = LogisticRegression(**params)
    model.fit(X_train, y_train)

    # 5. Evaluate
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

    # 6. Log confusion matrix as an artifact
    fig, ax = plt.subplots()
    ConfusionMatrixDisplay.from_predictions(
        y_test, predictions, ax=ax
    )
    fig.tight_layout()
    fig.savefig("confusion_matrix.png")
    plt.close(fig)

    mlflow.log_artifact("confusion_matrix.png")

    # 7. Save the model in MLflow
    mlflow.sklearn.log_model(
        sk_model=model,
        name="iris_classifier",
        input_example=X_train.head(3),
    )

    print("Metrics:", metrics)
    print("Run ID:", mlflow.active_run().info.run_id)

print("Experiment completed.")