import math

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(
    title="Podman Inference API",
    version="1.0.0",
    description="A simple demonstration inference endpoint",
)


class PredictionRequest(BaseModel):
    feature_1: float = Field(ge=-100, le=100)
    feature_2: float = Field(ge=-100, le=100)


class PredictionResponse(BaseModel):
    probability: float
    prediction: int
    model: str


@app.get("/")
def root():
    return {"message": "Podman Inference API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest):
    # Demonstration only: logistic-regression-style scoring.
    # Replace these coefficients with a real trained model in production.
    z = 0.8 * request.feature_1 - 0.5 * request.feature_2 + 0.2
    z = max(-500.0, min(500.0, z))
    probability = 1.0 / (1.0 + math.exp(-z))

    return {
        "probability": round(probability, 6),
        "prediction": int(probability >= 0.5),
        "model": "demo-logistic-score-v1",
    }
