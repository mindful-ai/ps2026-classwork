import hashlib
import json
import math
import os
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field


REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    redis_client = redis.from_url(
        REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
        socket_connect_timeout=2,
        socket_timeout=2,
    )
    yield
    if redis_client is not None:
        await redis_client.aclose()


app = FastAPI(
    title="Podman Inference API",
    version="1.1.0",
    lifespan=lifespan,
)


class PredictionRequest(BaseModel):
    feature_1: float = Field(ge=-100, le=100)
    feature_2: float = Field(ge=-100, le=100)


def infer(feature_1: float, feature_2: float):
    z = 0.8 * feature_1 - 0.5 * feature_2 + 0.2
    z = max(-500.0, min(500.0, z))
    probability = 1.0 / (1.0 + math.exp(-z))
    return {
        "probability": round(probability, 6),
        "prediction": int(probability >= 0.5),
        "model": "demo-logistic-score-v1",
    }


@app.get("/")
def root():
    return {"message": "Podman Inference API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    try:
        await redis_client.ping()
        return {"status": "ready", "redis": "connected"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Redis is unavailable") from exc


@app.post("/predict")
async def predict(request: PredictionRequest):
    # Stable cache key for the normalized input values.
    normalized = json.dumps(
        {
            "feature_1": request.feature_1,
            "feature_2": request.feature_2,
        },
        sort_keys=True,
    )
    key = "prediction:" + hashlib.sha256(normalized.encode()).hexdigest()

    try:
        cached = await redis_client.get(key)
        if cached:
            result = json.loads(cached)
            result["cache"] = "hit"
            return result
    except Exception:
        # Keep inference available if the cache is temporarily unavailable.
        pass

    result = infer(request.feature_1, request.feature_2)

    try:
        await redis_client.set(key, json.dumps(result), ex=300)
        result["cache"] = "miss"
    except Exception:
        result["cache"] = "unavailable"

    return result
