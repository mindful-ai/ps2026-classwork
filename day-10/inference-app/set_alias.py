# This script demonstrates how to set an alias for a specific version of a registered model in MLflow.
import mlflow

TRACKING_URI = "http://127.0.0.1:5000"

client = mlflow.MlflowClient(
    tracking_uri=TRACKING_URI
)

MODEL_NAME = "IrisClassifier"
ALIAS = "champion"
VERSION = "3"

# Assign the alias to model version 3
client.set_registered_model_alias(
    name=MODEL_NAME,
    alias=ALIAS,
    version=VERSION,
)

# Verify the alias assignment
model_version = client.get_model_version_by_alias(
    name=MODEL_NAME,
    alias=ALIAS,
)

print("Alias assigned successfully.")
print("Model:", model_version.name)
print("Version:", model_version.version)
print("Run ID:", model_version.run_id)
