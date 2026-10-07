
# 🧠 ML Deployment & MLOps: Concepts, Examples, and a Medical Case Study

A practitioner’s guide to deploying machine learning systems with **FastAPI**, **Streamlit**, **Docker/Kubernetes**, and **MLOps**. Includes concrete, copy‑ready snippets and a complete **Heart Disease Prediction** case study.

---

## 📚 Table of Contents

1. [Deployment Process](#1-deployment-process)
2. [Role of Cloud Technologies](#2-role-of-cloud-technologies)
3. [Importance of MLOps](#3-importance-of-mlops)
4. [Challenges in Deployment](#4-challenges-in-deployment)
5. [API Fundamentals](#5-api-fundamentals)
6. [Creating Prediction Endpoints & Why They Matter](#6-creating-prediction-endpoints--why-they-matter)
7. [Low-Latency & High-Throughput Considerations](#7-low-latency--high-throughput-considerations)
8. [🏥 Case Study: Heart Disease Prediction System](#-case-study-heart-disease-prediction-system)
9. [Appendix: Copy‑Ready Snippets](#appendix-copyready-snippets)

---

## 1. Deployment Process

**Goal:** Make a trained model reliably accessible to users/systems in production.

### 1.1 Canonical Steps
1. **Train & Evaluate**: Build the model offline with historical data.
2. **Package Artifact**: Save as `model.pkl`/`model.onnx` with the **exact feature order** and preprocessing steps.
3. **Wrap with API**: Expose `POST /predict` (and health/metadata endpoints) with **FastAPI**.
4. **Containerize**: Create a **Docker** image (app + model + deps).
5. **Release & Run**: Orchestrate with **Kubernetes** / serverless containers. Add **load balancer** + **TLS**.
6. **Observe**: Logs, metrics, traces; monitor **drift** & **accuracy**; add alerts.
7. **Iterate**: A/B or canary new models, rollback fast if needed.

### 1.2 Minimal FastAPI Wrapper (sync, CPU)
```python
from fastapi import FastAPI
from pydantic import BaseModel
import joblib, numpy as np

app = FastAPI(title="Heart Predictor")
model, feature_names = joblib.load("heart_model.pkl")  # (clf, columns)

class HeartInput(BaseModel):
    Age:int; Sex:int; ChestPain:int; RestBP:int; Chol:int
    MaxHR:int; ExAng:int; Oldpeak:float; Slope:int; Ca:int; Thal:int

@app.get("/health")
def health(): return {"status":"ok"}

@app.post("/predict")
def predict(x: HeartInput):
    arr = np.array([[x.Age,x.Sex,x.ChestPain,x.RestBP,x.Chol,
                     x.MaxHR,x.ExAng,x.Oldpeak,x.Slope,x.Ca,x.Thal]])
    y = int(model.predict(arr)[0])
    return {"prediction": y, "label": "Heart Disease" if y else "No Heart Disease"}
```

### 1.3 Containerization & Run
- **Dockerfile** in [Appendix](#dockerfile-slim-fastapi).
- Local run: `docker build -t heart-api . && docker run -p 8000:8000 heart-api`

### 1.4 Release Strategies
- **Blue/Green**: Two environments; switch traffic when green is healthy.
- **Canary**: Shift 1–5% traffic to new model; expand if KPIs good.
- **Shadow**: Send a copy of production traffic to new model for offline eval.

---

## 2. Role of Cloud Technologies

### 2.1 Why Cloud?
- **Elasticity** (scale to peaks), **Reliability** (multi‑AZ), **Managed** ops (load balancing, TLS).
- **Integrated** observability, secrets, queues, serverless compute.

### 2.2 Service Mapping (Cheat Sheet)

| Capability | AWS | Azure | GCP |
|---|---|---|---|
| Containers (Serverless) | Fargate/ECS, App Runner | Container Apps | Cloud Run |
| Kubernetes | EKS | AKS | GKE |
| VM Compute | EC2 | VM Scale Sets | Compute Engine |
| Model Hosting | SageMaker | Azure ML | Vertex AI |
| Registry | ECR | ACR | GCR/Artifact Registry |
| Logs | CloudWatch | Monitor/Log Analytics | Cloud Logging |
| Metrics | CloudWatch | Monitor | Cloud Monitoring |
| Secrets | Secrets Manager | Key Vault | Secret Manager |
| Storage | S3 | Blob Storage | GCS |
| Queue/Async | SQS/SNS | Service Bus | Pub/Sub |

### 2.3 Compute Choices
- **Serverless containers (Cloud Run/App Runner)**: Simple, autoscale, pay‑per‑use.
- **Kubernetes**: Fine‑grained control, hybrid, cost‑efficient at scale.
- **Functions (Lambda/Cloud Functions)**: Great for lightweight inference, cold starts may hurt latency.

---

## 3. Importance of MLOps

### 3.1 Lifecycle
**Data → Train → Register → Deploy → Monitor → Trigger Retrain → Redeploy**

### 3.2 Core Components
- **Experiment tracking**: MLflow/W&B (metrics, params, artifacts)
- **Model Registry**: versioned models, stage transitions (Staging → Production)
- **CI/CD for ML**: tests, lint, security scan, docker build, deploy
- **Data/Feature Versioning**: DVC/LakeFS; **Feature Store** (Feast/Tecton)
- **Monitoring**: performance (AUC, recall), **data/label drift**, fairness
- **Governance**: lineage, approvals, PII handling, audit logs

### 3.3 Simple MLflow Flow
1. Log experiments and metrics.
2. Register best model as `HeartRF:v17 (Production)`.
3. Deploy via FastAPI pulling by **registry URI** (not local file).

---

## 4. Challenges in Deployment

- **Data/Concept Drift**: Input distribution or clinical practice changes.
- **Latency & Throughput**: P99 guarantees under load.
- **Reproducibility**: Env pinning (`requirements.txt`, Docker digest).
- **Security & Compliance**: HIPAA/GDPR, RBAC, encryption, audit.
- **Versioning & Rollbacks**: Multiple model versions live.
- **Explainability**: Clinicians need reason codes (SHAP/LIME).
- **Cost**: Over‑provisioning or expensive accelerators.

**Mitigations:** canary deploys, drift alarms, retraining pipelines, structured logs, RBAC & VPCs, autoscaling.

---

## 5. API Fundamentals

### 5.1 REST Basics
- **Endpoints** (`/predict`, `/health`, `/metadata`, `/feedback`)
- **Methods**: `GET`, `POST`
- **Contracts**: input/output schemas with **Pydantic**
- **Versioning**: `/v1/predict` (don’t break clients)
- **Docs**: OpenAPI via FastAPI `/docs`

### 5.2 Example Schemas
```python
from pydantic import BaseModel, Field
from typing import List, Optional

class HeartInput(BaseModel):
    Age:int = Field(ge=18, le=100)
    Sex:int; ChestPain:int; RestBP:int; Chol:int
    MaxHR:int; ExAng:int; Oldpeak:float; Slope:int; Ca:int; Thal:int

class HeartPrediction(BaseModel):
    prediction:int
    label:str
    probability: Optional[float] = None
```

### 5.3 Helpful Endpoints
- `GET /health` → liveness/readiness
- `GET /metadata` → model version, trained_at
- `POST /predict` → single prediction
- `POST /predict-batch` → CSV upload → JSON/CSV results
- `POST /feedback` → capture clinician overrides for retraining

---

## 6. Creating Prediction Endpoints & Why They Matter

**Benefits:** standardization, reuse across apps, decoupled clients, controlled rollout, central monitoring, and governance.

### 6.1 Batch Prediction (CSV Upload)
```python
from fastapi import FastAPI, UploadFile, File
import pandas as pd, io, joblib

app = FastAPI()
model, columns = joblib.load("heart_model.pkl")

@app.post("/predict-batch")
async def predict_batch(file: UploadFile = File(...)):
    df = pd.read_csv(io.BytesIO(await file.read()))
    df = df[columns]  # enforce schema/order
    preds = model.predict(df.values).tolist()
    return {"n": len(preds), "predictions": preds}
```

---

## 7. Low-Latency & High-Throughput Considerations

### 7.1 Define SLOs (example)
- **Latency**: p50 ≤ 60 ms, p95 ≤ 150 ms, p99 ≤ 250 ms (single inference)
- **Availability**: 99.9%
- **Throughput**: sustain 500 RPS with 5 replicas

### 7.2 App‑Level Optimizations
- Load model **once** at startup; avoid per‑request disk I/O.
- Use **orjson** response class, **uvloop** (if applicable), Pydantic v2.
- Precompute encoders; move heavy preprocessing out of hot path.
- Consider **ONNX** + onnxruntime, or distilled models to speed up.
- Async I/O; threadpool for CPU-bound steps with multiple workers.

### 7.3 Infra‑Level Optimizations
- **Gunicorn + Uvicorn workers**: `workers = cores * 2 + 1`
- Autoscale on CPU/RPS; HPA in Kubernetes.
- Place service close to users; enable HTTP keep‑alive & compression.
- Use cache (Redis) for repeated queries; consider **result TTL**.

### 7.4 Capacity Planning (Little’s Law)
`Concurrency ≈ Throughput × Latency`  
If p95 latency = 120 ms (0.12s) and target 200 RPS, concurrency ≈ 24 ongoing requests → size worker pool and replicas accordingly.

---

## 🏥 Case Study: Heart Disease Prediction System

### 8.1 Background
A healthcare network wants real‑time support to flag **heart disease risk** at triage. Data comes from electronic health records (EHR) across multiple clinics.

### 8.2 Dataset
Features (example): Age, Sex, ChestPain, RestBP, Chol, MaxHR, ExAng, Oldpeak, Slope, Ca, Thal.  
Target: `AHD` (1 = disease, 0 = no disease).

### 8.3 Requirements & SLOs
- **Functional**: `POST /predict`, `POST /predict-batch`, `GET /metadata`, `POST /feedback`
- **SLOs**: p99 ≤ 250 ms, 99.9% availability, ≥ 85% recall (clinical priority)
- **Security**: OAuth2/JWT; network‑isolated (VPC); audit logging
- **Compliance**: PHI encrypted at rest (KMS) and in transit (TLS); access logs retained 365 days

### 8.4 Architecture (textual)
**Client (Streamlit/EMR UI)** → **API Gateway / LB (TLS)** → **FastAPI Inference Pods** → **Model Artifact Store (S3/Registry)**  
Observability: **Prometheus/Grafana + ELK/CloudWatch**. CI/CD: **GitHub Actions**. Registry: **MLflow**.

### 8.5 Implementation Plan
1. **Modeling**: Train RF/LogReg; log metrics in **MLflow**; register model v1.
2. **API**: FastAPI with `/predict`, `/health`, `/metadata`, `/feedback`; JSON logs.
3. **Container**: Docker + slim base; non‑root user; multi‑stage build.
4. **Deploy**: Helm chart to AKS/EKS/GKE; HPA enabled.
5. **Observe**: Prometheus metrics (latency, RPS), alerts on p99 & error rate.
6. **Drift**: KS test/PSI on inputs; alert when > threshold; trigger retrain job.
7. **Security**: OAuth2; rotate secrets; restrict egress; WAF at LB.
8. **Rollout**: Canary 5% traffic; evaluate recall on clinician‑verified subset; promote to 100% if KPIs pass.

### 8.6 Logging & Monitoring
- **Structured JSON logs** with request_id, model_version, latency_ms.
- **Metrics**: `inference_requests_total`, `inference_latency_ms_bucket`, `drift_score`.
- **Tracing**: OpenTelemetry to correlate UI → API → model calls.

### 8.7 Testing Strategy
- **Unit**: feature order, missing value handling
- **Contract**: schema compatibility (Pydantic, OpenAPI)
- **Load**: Locust/K6 to 500 RPS, ensure p99 ≤ 250 ms
- **Security**: authZ/authN tests, dependency scans (pip‑audit, Trivy)

### 8.8 Rollout & Ops
- Stage → Canary (5%) → Production (100%)
- Daily dashboards: traffic, latency, error rate, top inputs
- Weekly: model KPI review (recall/precision), drift report
- Quarterly: re‑baseline with new labeled data

### 8.9 Cost Levers
- Right‑size pods; autoscale to zero on nights (if allowed)
- Use spot nodes for non‑prod
- Optimize model to reduce CPU/GPU time

### 8.10 Lessons Learned
- Enforce feature schema; subtle order issues cause silent errors
- Always expose `/metadata` & `/health`
- Canary every model; accept small latency regressions if recall improves (clinical priority)

---

## Appendix: Copy‑Ready Snippets

### Dockerfile (Slim FastAPI)
```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .
# Non-root user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Gunicorn + Uvicorn workers for concurrency
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "main:app", \
     "--bind", "0.0.0.0:8000", "--workers", "3", "--threads", "2", "--timeout", "60"]
```

### requirements.txt
```
fastapi
uvicorn[standard]
joblib
numpy
pandas
orjson
```
*(add scikit-learn/onnxruntime if needed)*

### Kubernetes Deployment & Service (basic)
```yaml
apiVersion: apps/v1
kind: Deployment
metadata: { name: heart-api, labels: { app: heart-api } }
spec:
  replicas: 3
  selector: { matchLabels: { app: heart-api } }
  template:
    metadata: { labels: { app: heart-api } }
    spec:
      containers:
      - name: heart-api
        image: registry.example.com/heart-api:1.0.0
        ports: [{containerPort: 8000}]
        resources:
          requests: { cpu: "250m", memory: "256Mi" }
          limits:   { cpu: "1000m", memory: "1Gi" }
        readinessProbe:
          httpGet: { path: /health, port: 8000 }
          initialDelaySeconds: 5
        livenessProbe:
          httpGet: { path: /health, port: 8000 }
          initialDelaySeconds: 10
---
apiVersion: v1
kind: Service
metadata: { name: heart-api-svc }
spec:
  selector: { app: heart-api }
  ports: [{ port: 80, targetPort: 8000 }]
  type: ClusterIP
```

### GitHub Actions (CI → Build & Push Docker)
```yaml
name: ci
on: [push]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with: { python-version: "3.11" }
    - run: pip install -r requirements.txt
    - run: python -m pip install pip-audit && pip-audit || true
    - uses: docker/setup-buildx-action@v3
    - uses: docker/login-action@v3
      with: { registry: ghcr.io, username: ${{ github.actor }}, password: ${{ secrets.GITHUB_TOKEN }} }
    - uses: docker/build-push-action@v6
      with:
        context: .
        push: true
        tags: ghcr.io/${{ github.repository }}:latest
```

### FastAPI with Structured JSON Logging
```python
import json, time, logging
from fastapi import FastAPI, Request
from fastapi.responses import ORJSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("heart-api")

app = FastAPI(default_response_class=ORJSONResponse)
model_version = "rf-1.0.3"

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    dur = int((time.time() - start) * 1000)
    logger.info(json.dumps({
        "event":"request", "path": request.url.path, "status": response.status_code,
        "latency_ms": dur, "model_version": model_version
    }))
    return response

@app.get("/metadata")
def meta(): return {"model_version": model_version}
```

### Prometheus Metrics Example
```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response

requests_total = Counter("inference_requests_total", "Total inference requests")
latency = Histogram("inference_latency_ms", "Latency (ms)")

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.post("/predict")
@latency.time()  # measure
def predict(x: HeartInput):
    requests_total.inc()
    # ... inference as before ...
```

### Batch Endpoint with File Response
```python
from fastapi.responses import StreamingResponse
import io, csv

@app.post("/predict-batch-csv")
async def predict_batch_csv(file: UploadFile = File(...)):
    df = pd.read_csv(io.BytesIO(await file.read()))
    preds = model.predict(df[feature_names].values)
    out = io.StringIO()
    writer = csv.writer(out); writer.writerow(["prediction"]); writer.writerows([[p] for p in preds])
    out.seek(0)
    return StreamingResponse(iter([out.getvalue()]), media_type="text/csv",
                             headers={"Content-Disposition":"attachment; filename=preds.csv"})
```

---

## ✅ How to Use This Document
- Use sections **1–7** as lecture notes with copy‑ready code.
- Use **Case Study** as the classroom project narrative and checklist.
- Use **Appendix** to bootstrap repos quickly for demos/labs.

---


