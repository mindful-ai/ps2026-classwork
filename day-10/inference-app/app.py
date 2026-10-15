# Imports
import mlflow
import mlflow.pyfunc
import pandas as pd
import numpy as np

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# MLflow configuration

# Connect to the MLflow tracking server


TRACKING_URI = "http://localhost:5000"
MODEL_NAME = "IrisClassifier"
MODEL_ALIAS = "champion"

mlflow.set_tracking_uri(TRACKING_URI)

# Load the model from the MLflow model registry

print(f"Loading model '{MODEL_NAME}' with alias '{MODEL_ALIAS}' from MLflow model registry...")

MODEL_URI = f"models:/{MODEL_NAME}@{MODEL_ALIAS}"

model = mlflow.pyfunc.load_model(MODEL_URI)

# FastAPI application setup

app = FastAPI(title="Iris Flower Classification API", version="1.0.0")

# Pydantic model for input validation

class IrisFeatures(BaseModel):
    sepal_length: float = Field(..., ge=0)
    sepal_width: float = Field(..., ge=0)
    petal_length: float = Field(..., ge=0)
    petal_width: float = Field(..., ge=0)

# Iris flower features for prediction

SPECIES = ["setosa", "versicolor", "virginica"]

# Home endpoint

@app.get("/")
def home():
    return {"message": "Welcome to the Iris Flower Classification API!"}

# Endpoint for health check

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Endpoint for model information retrieval

@app.get("/model-info")
def get_model_info():
    try:
        # model_info = mlflow.registered_model.get_registered_model(MODEL_NAME)
        # return {
        #     "model_name": model_info.name,
        #     "model_versions": [version.version for version in model_info.latest_versions],
        # }
        client = mlflow.MlflowClient(tracking_uri=TRACKING_URI)
        versions = client.get_model_version_by_alias(MODEL_NAME, MODEL_ALIAS)
        return {
            "model_name": MODEL_NAME, 
            "model_versions": [versions.version],
            "registered_model_uri": MODEL_URI,
            "run_id": versions.run_id,
            "resolved_version": versions.version
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Endpoint for making predictions using the registered model

@app.post("/predict")
def predict(features: IrisFeatures):

    # Match the feature names and order used in training.
    input_data = pd.DataFrame(
        [[
            features.sepal_length,
            features.sepal_width,
            features.petal_length,
            features.petal_width,
        ]],
        columns=[
            "sepal length (cm)",
            "sepal width (cm)",
            "petal length (cm)",
            "petal width (cm)",
        ],
    )

    try:
        prediction = int(
            model.predict(input_data)[0]
        )

        if prediction < 0 or prediction >= len(SPECIES):
            raise ValueError(
                f"Unexpected class index: {prediction}"
            )

        return {
            "prediction": prediction,
            "species": SPECIES[prediction],
            "model_uri": MODEL_URI,
            "input": features.model_dump(),
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {exc}",
        )
