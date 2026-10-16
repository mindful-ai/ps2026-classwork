

### DAG Setup

```python
from datetime import datetime
from airflow.decorators import dag, task
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import joblib
import os
import requests
import subprocess
import time

MODEL_PATH = "/usr/local/airflow/include/iris_model.pkl"

@dag(
    dag_id="ml_pipeline_with_endpoint",
    start_date=datetime(2024, 1, 1),
    schedule="@once",
    catchup=False,
    tags=["ml", "endpoint", "workshop"],
)
def ml_pipeline_with_endpoint():

    @task
    def load_data():
        iris = load_iris(as_frame=True)
        df = iris.frame
        print(f"Dataset loaded with shape {df.shape}")
        return df.to_dict()

    @task
    def preprocess(data: dict):
        df = pd.DataFrame.from_dict(data)
        X = df.drop("target", axis=1)
        y = df["target"]
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        return {
            "X_train": X_train.to_dict(),
            "X_test": X_test.to_dict(),
            "y_train": y_train.to_list(),
            "y_test": y_test.to_list(),
        }

    @task
    def train(data: dict):
        X_train = pd.DataFrame.from_dict(data["X_train"])
        y_train = data["y_train"]

        model = LogisticRegression(max_iter=200)
        model.fit(X_train, y_train)

        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        joblib.dump(model, MODEL_PATH)
        print(f"Model saved at {MODEL_PATH}")
        return MODEL_PATH

    @task
    def evaluate(data: dict, model_path: str):
        X_test = pd.DataFrame.from_dict(data["X_test"])
        y_test = data["y_test"]

        model = joblib.load(model_path)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"Model Accuracy = {acc:.2f}")
        return acc

    @task
    def deploy(model_path: str):
        # Launch FastAPI app in background (simulate deployment)
        app_code = f"""
from fastapi import FastAPI
import joblib
import numpy as np

app = FastAPI()
model = joblib.load("{model_path}")

@app.post("/predict")
def predict(features: list[float]):
    prediction = model.predict([features])
    return {{ "prediction": int(prediction[0]) }}
"""
        app_file = "/usr/local/airflow/include/app.py"
        with open(app_file, "w") as f:
            f.write(app_code)

        subprocess.Popen(["uvicorn", "include.app:app", "--host", "0.0.0.0", "--port", "8000"])
        time.sleep(3)  # give server time to start
        print("FastAPI app deployed at http://localhost:8000/predict")
        return "http://localhost:8000/predict"

    @task
    def predict(endpoint: str):
        sample_input = [5.1, 3.5, 1.4, 0.2]  # Iris sample features
        response = requests.post(endpoint, json=sample_input)
        print(f"Prediction Response: {response.json()}")

    # DAG Orchestration
    raw_data = load_data()
    processed_data = preprocess(raw_data)
    model_path = train(processed_data)
    evaluate(processed_data, model_path)
    endpoint = deploy(model_path)
    predict(endpoint)


dag = ml_pipeline_with_endpoint()
```

------------------------------------------------------------------------------

### Alternative Code - Also checks for FastAPI file

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import pickle
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

# Paths
MODEL_PATH = "/usr/local/airflow/include/iris_model.pkl"
API_FILE_PATH = "/usr/local/airflow/include/iris_api.py"

# ---------------------------
# Define FastAPI app code ONCE
# ---------------------------
api_code = f"""
from fastapi import FastAPI
import pickle
import numpy as np

app = FastAPI()

# Load model once
with open("{MODEL_PATH}", "rb") as f:
    model = pickle.load(f)

@app.get("/")
def home():
    return {{"message": "Iris prediction API is running!"}}

@app.post("/predict")
def predict(features: list):
    prediction = model.predict([features])
    return {{"prediction": int(prediction[0])}}
"""

# Step 1: Load and preprocess dataset
def load_and_preprocess():
    iris = load_iris()
    X_train, X_test, y_train, y_test = train_test_split(
        iris.data, iris.target, test_size=0.2, random_state=42
    )
    return X_train, X_test, y_train, y_test

# Step 2: Train and save model
def train_and_save_model():
    X_train, X_test, y_train, y_test = load_and_preprocess()
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    print(f"✅ Model saved at {MODEL_PATH}")

# Step 3: Create FastAPI app (only once)
def create_fastapi_app():
    if not os.path.exists(API_FILE_PATH):  # Avoid overwriting
        with open(API_FILE_PATH, "w") as f:
            f.write(api_code)
        print(f"✅ FastAPI app created at {API_FILE_PATH}")
    else:
        print("ℹ️ FastAPI app already exists. Skipping file creation.")

# Step 4: Start FastAPI server if not running
def start_fastapi():
    is_running = os.system("pgrep -f 'uvicorn iris_api:app' > /dev/null 2>&1")
    if is_running != 0:
        os.system(f"nohup uvicorn iris_api:app --host 0.0.0.0 --port 8000 --reload &")
        print("✅ FastAPI server started on port 8000")
    else:
        print("ℹ️ FastAPI server already running")

# ---------------------------
# Airflow DAG
# ---------------------------
with DAG(
    dag_id="ml_pipeline_with_fastapi_once",
    start_date=datetime(2024, 1, 1),
    schedule_interval="@weekly",
    catchup=False
) as dag:

    train_model_task = PythonOperator(
        task_id="train_model",
        python_callable=train_and_save_model
    )

    create_api_task = PythonOperator(
        task_id="create_api_file",
        python_callable=create_fastapi_app
    )

    start_api_task = PythonOperator(
        task_id="start_api_server",
        python_callable=start_fastapi
    )

    train_model_task >> create_api_task >> start_api_task

```

------------------------------------------------------------------------------

### Testing the end-point

```bash

curl -X POST "http://localhost:8000/predict" -H "Content-Type: application/json" -d "[6.1, 2.8, 4.7, 1.2]"

curl -X POST "http://localhost:9000/predict" -H "Content-Type: application/json" -d "{\"features\": [6.1, 2.8, 4.7, 1.2]}"


```

### See the output of print statements

Go to the Airflow UI (Astronomer exposes it at http://localhost:8080 by default when you run astro dev start).

Navigate to:
DAGs → Your DAG → Graph / Tree View → Click on a task → Logs tab

In the logs, you’ll see your print() outputs along with other Airflow system logs.

#### You can also see the logs

- astro dev logs --scheduler
- astro dev logs --webserver
- astro dev logs
