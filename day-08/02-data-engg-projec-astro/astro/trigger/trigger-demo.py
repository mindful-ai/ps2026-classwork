
import requests

AIRFLOW_URL = "http://localhost:8080"
DAG_ID = "ecommerce_data_pipeline"

# Use the credentials configured for your local Airflow instance.
USERNAME = "admin"
PASSWORD = "admin"

url = f"{AIRFLOW_URL}/api/v1/dags/{DAG_ID}/dagRuns"

response = requests.post(
    url,
    auth=(USERNAME, PASSWORD),
    json={
        "conf": {
            "triggered_by": "external_python_script"
        }
    },
    timeout=30,
)

response.raise_for_status()

result = response.json()
print("DAG triggered successfully!")
print("Run ID:", result.get("dag_run_id"))
print("State:", result.get("state"))
