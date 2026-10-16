# Kubernetes Workshop: Podman + Kind + FastAPI

**Objective:** Build a FastAPI inference service, package it with Podman, deploy it to a local Kubernetes cluster using Kind, and test scaling, self-healing, rolling updates, and rollback.

Commands are written for **Windows PowerShell**. Most commands also work on macOS/Linux with small shell or runtime differences.

## Workshop overview

1. Create a FastAPI application.
2. Build and test a Podman container.
3. Create a Kind Kubernetes cluster.
4. Load the image into Kind.
5. Deploy using `deployment.yaml` and `service.yaml`.
6. Test the API, scaling, self-healing, rolling updates, and rollback.

## Step 1 — Create the project

```powershell
mkdir inference-workshop
cd inference-workshop
mkdir app
```

Create this structure:

```text
inference-workshop/
├── app/
│   └── main.py
├── requirements.txt
├── Containerfile
├── deployment.yaml
└── service.yaml
```

## Step 2 — Create the FastAPI application

Create `app/main.py`:

```python
from fastapi import FastAPI
from pydantic import BaseModel
import math

app = FastAPI(title="Podman Inference API")


class PredictionInput(BaseModel):
    feature_1: float
    feature_2: float


@app.get("/")
def root():
    return {
        "message": "Podman Inference API",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(data: PredictionInput):
    # For feature_1=2.5 and feature_2=1.2, score=1.6.
    score = 0.5 * data.feature_1 + 0.5 * data.feature_2 - 0.25
    probability = 1 / (1 + math.exp(-score))

    return {
        "probability": round(probability, 6),
        "prediction": int(probability >= 0.5),
        "model": "demo-logistic-score-v1"
    }
```

This is a deterministic demo inference function, not a trained ML model. The formula above returns a probability of approximately `0.832018` for the sample input.

## Step 3 — Add dependencies

Create `requirements.txt`:

```text
fastapi
uvicorn[standard]
```

## Step 4 — Create the Containerfile

Create `Containerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 5 — Build the image with Podman

Run from the project root:

```powershell
podman build -t localhost/inference-api:1.0 -f Containerfile .
podman images
```

## Step 6 — Test the container locally

Start the container:

```powershell
podman run -d --name inference-api -p 8000:8000 localhost/inference-api:1.0
```

Test the endpoints:

```powershell
curl.exe http://localhost:8000/
curl.exe http://localhost:8000/health
```

Test inference:

```powershell
curl.exe -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{\"feature_1\":2.5,\"feature_2\":1.2}'
```

Expected prediction:

```json
{
  "probability": 0.832018,
  "prediction": 1,
  "model": "demo-logistic-score-v1"
}
```

Check logs and remove the local container:

```powershell
podman logs inference-api
podman rm -f inference-api
```

## Step 7 — Start the Kind cluster

Check existing clusters:

```powershell
kind get clusters
```

If you do not already have a cluster, create one:

```powershell
kind create cluster --name ps-cluster
```

Check the cluster:

```powershell
kubectl config current-context
kubectl cluster-info
kubectl get nodes
kubectl get pods -A
```

Wait until the node status is `Ready`.

> If you already have a cluster named differently, use that name in the following Kind commands instead of `ps-cluster`.

## Step 8 — Load the image into Kind

```powershell
kind load docker-image localhost/inference-api:1.0 --name ps-cluster
kubectl get nodes
```

Kind needs the image loaded into its node because the image was built locally and is not being pulled from a remote registry.

## Step 9 — Create `deployment.yaml`

Create `deployment.yaml` in the project root:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-api
spec:
  replicas: 2
  selector:
    matchLabels:
      app: inference-api
  template:
    metadata:
      labels:
        app: inference-api
    spec:
      containers:
        - name: inference-api
          image: localhost/inference-api:1.0
          imagePullPolicy: IfNotPresent
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 20
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
```

Key points:

- `replicas: 2` requests two application Pods.
- `imagePullPolicy: IfNotPresent` lets Kubernetes use the image loaded into Kind.
- Readiness probes determine whether a Pod is ready to receive traffic.
- Liveness probes help Kubernetes detect and restart an unhealthy container.
- Resource requests and limits define the container's resource requirements and caps.

## Step 10 — Create `service.yaml`

Create `service.yaml` in the project root:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: inference-api
spec:
  type: ClusterIP
  selector:
    app: inference-api
  ports:
    - name: http
      port: 8000
      targetPort: 8000
      protocol: TCP
```

The Service provides a stable network endpoint and sends traffic to Pods with the matching label.

## Step 11 — Deploy the application

Run from the directory containing both YAML files:

```powershell
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
```

Inspect the resources:

```powershell
kubectl get deployments
kubectl get replicasets
kubectl get pods -o wide
kubectl get services
kubectl rollout status deployment/inference-api
```

Expected: two available replicas and Pods in the `Running` state.

If anything fails, inspect it before continuing:

```powershell
kubectl describe deployment inference-api
kubectl describe pods
kubectl get events --sort-by=.metadata.creationTimestamp
```

## Step 12 — Access and test the API

Start port forwarding in one terminal:

```powershell
kubectl port-forward service/inference-api 8000:8000
```

Keep this terminal open. In another terminal, run:

```powershell
curl.exe http://localhost:8000/
curl.exe http://localhost:8000/health
```

Test inference:

```powershell
curl.exe -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{\"feature_1\":2.5,\"feature_2\":1.2}'
```

Expected response:

```json
{
  "probability": 0.832018,
  "prediction": 1,
  "model": "demo-logistic-score-v1"
}
```

## Step 13 — Scale the application

Scale from two Pods to four:

```powershell
kubectl scale deployment/inference-api --replicas=4
kubectl get deployments
kubectl get pods -o wide
kubectl rollout status deployment/inference-api
```

Scale back to two:

```powershell
kubectl scale deployment/inference-api --replicas=2
kubectl get pods
```

## Step 14 — Test self-healing

List the Pods and choose one Pod name:

```powershell
kubectl get pods
```

Delete one Pod, replacing `POD_NAME` with its actual name:

```powershell
kubectl delete pod POD_NAME
```

Watch Pod replacement:

```powershell
kubectl get pods -w
```

In another terminal, verify the desired replica count:

```powershell
kubectl get deployment inference-api
```

Expected: Kubernetes creates a replacement Pod to maintain the desired replica count.

## Step 15 — Test a rolling update

For a meaningful version change, edit `app/main.py` and change the model identifier to `demo-logistic-score-v2`.

Build version 1.1:

```powershell
podman build -t localhost/inference-api:1.1 -f Containerfile .
```

Load it into Kind:

```powershell
kind load docker-image localhost/inference-api:1.1 --name ps-cluster
```

Update the Deployment:

```powershell
kubectl set image deployment/inference-api inference-api=localhost/inference-api:1.1
```

Monitor the rollout:

```powershell
kubectl rollout status deployment/inference-api
kubectl get pods
kubectl rollout history deployment/inference-api
```

Test the API again through the port-forward terminal. The response should show `demo-logistic-score-v2`.

## Step 16 — Roll back the update

Revert to the previous Deployment revision:

```powershell
kubectl rollout undo deployment/inference-api
```

Verify:

```powershell
kubectl rollout status deployment/inference-api
kubectl describe deployment inference-api
kubectl rollout history deployment/inference-api
```

Test the API again. The response should show the previous model identifier.

## Step 17 — Inspect logs and troubleshoot

```powershell
kubectl logs deployment/inference-api
kubectl logs deployment/inference-api --all-pods=true
kubectl describe deployment inference-api
kubectl get events --sort-by=.metadata.creationTimestamp
kubectl get pods -o wide
kubectl get endpointslice
```

If a Pod fails, replace `POD_NAME` with its actual name:

```powershell
kubectl describe pod POD_NAME
kubectl logs POD_NAME
```

## Step 18 — Clean up

Delete the Kubernetes resources:

```powershell
kubectl delete -f service.yaml
kubectl delete -f deployment.yaml
```

Delete the Kind cluster when it is no longer needed:

```powershell
kind delete cluster --name ps-cluster
```

Optionally remove local images:

```powershell
podman rmi localhost/inference-api:1.0
podman rmi localhost/inference-api:1.1
```

## Workshop testing checklist

- [ ] FastAPI runs locally in Podman.
- [ ] Health and prediction endpoints work.
- [ ] Kind cluster is `Ready`.
- [ ] Image loads into Kind.
- [ ] `deployment.yaml` creates two healthy Pods.
- [ ] `service.yaml` exposes the application.
- [ ] Port-forwarded API tests pass.
- [ ] Scaling from two to four replicas works.
- [ ] Deleting a Pod triggers replacement.
- [ ] Rolling update to version 1.1 succeeds.
- [ ] Rollback restores the previous revision.
- [ ] Logs and troubleshooting commands work.

## Notes

- The demo prediction endpoint uses a fixed mathematical formula, not a trained model.
- If you use a cluster with a name other than `ps-cluster`, update the `kind load` and `kind delete` commands accordingly.
- Keep the port-forward terminal open while testing API requests.
- After the workshop has been tested, this file can be expanded into a full manual with verified outputs and troubleshooting notes.
