# fastapi_app.py
from fastapi import FastAPI
from pydantic import BaseModel
import pickle

# Load model
with open("artifacts/heart_pipeline.pkl", "rb") as f:
    model = pickle.load(f)

app = FastAPI(title="Heart Disease Prediction API")

# Input schema
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

@app.post("/predict")
def predict(data: HeartData):
    features = [[
        data.age, data.sex, data.cp, data.trestbps, data.chol,
        data.fbs, data.restecg, data.thalach, data.exang,
        data.oldpeak, data.slope, data.ca, data.thal
    ]]
    prediction = model.predict(features)[0]
    result = "Heart Disease Detected" if prediction == 1 else "No Heart Disease"
    return {"prediction": int(prediction), "result": result}
