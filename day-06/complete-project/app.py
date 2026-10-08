from typing import Dict

import pickle
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel


FEATURES = [
    "age", "sex", "cp", "trestbps", "chol", "fbs",
    "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal"
]


# Load model
with open("artifacts/heart_pipeline.pkl", "rb") as f:
    model = pickle.load(f)


app = FastAPI(title="Heart Disease Prediction API")


class HeartData(BaseModel):
    age: int
    sex: int
    cp: int
    trestbps: int
    chol: int
    fbs: int
    restecg: int
    thalach: int
    exang: int
    oldpeak: float
    slope: int
    ca: int
    thal: int


@app.get("/")
def root():
    return {"message": "Heart Disease Prediction API is running"}


@app.post("/predict")
def predict(data: HeartData):
    # IMPORTANT:
    # The model was fitted with named DataFrame columns.
    # Use the same names and order at prediction time.
    features = pd.DataFrame([data.model_dump()])[FEATURES]

    prediction = int(model.predict(features)[0])

    # Probability of the positive class (heart disease = 1)
    probabilities = model.predict_proba(features)[0]
    class_to_probability = dict(zip(model.classes_, probabilities))
    probability = float(class_to_probability[1])

    result = (
        "Heart Disease Detected"
        if prediction == 1
        else "No Heart Disease"
    )

    return {
        "prediction": prediction,
        "result": result,
        "probability": probability
    }
