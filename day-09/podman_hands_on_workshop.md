# Hands-on Podman Workshop: Containers, FastAPI, Compose, and Kubernetes

## Workshop overview

This workshop progresses through five labs. Each lab produces a working result before moving to the next.

1. Create and inspect your first container.
2. Practise essential Podman commands.
3. Build a FastAPI application exposing a simple ML-style inference endpoint.
4. Run the API and Redis as a multi-container application using Compose.
5. Deploy the application to local Kubernetes and scale the API.

### Supported platforms

- Windows 11 with Podman Desktop (PowerShell commands are provided where needed).
- macOS on Apple Silicon, including M5 (Terminal).
- The project code, `Containerfile`, Compose file, and Kubernetes manifests are shared across both platforms.

### Prerequisites

- Podman installed.
- Podman Desktop installed (recommended for this workshop).
- Podman machine running.
- Internet access to pull base images and Python packages.
- Python 3.11+ is useful for local testing but is not required to build or run the containers.
- For Lab 4, a Compose provider must be installed and available to `podman compose`.
- For Lab 5, use Podman Desktop's built-in Kind integration and have `kubectl` available.

Check the engine before beginning:

```bash
podman --version
podman machine list
podman info
```

If the machine is stopped:

```bash
podman machine start
```

On Windows, Podman Desktop's Kind integration requires Podman to be configured in rootful mode. Follow Podman Desktop's current Kind setup instructions if you plan to use Kind on Windows: https://podman-desktop.io/docs/kind

---

# Lab 1 — Create Your First Container

## Objective

Pull an image, create and run containers, inspect them, view logs, and remove them.

## Exercise 1.1 — Run hello-world

```bash
podman run --name hello-lab docker.io/library/hello-world
```

Expected result: a message explaining that the container engine successfully ran the test container.

Inspect the container:

```bash
podman ps
podman ps -a
podman inspect hello-lab
podman logs hello-lab
```

**Observe:** `podman ps` lists running containers; `podman ps -a` also lists stopped containers. The `hello-world` container exits after printing its message.

Remove it:

```bash
podman rm hello-lab
```

## Exercise 1.2 — Run a web server

```bash
podman run -d --name web-lab -p 8080:80 docker.io/library/nginx:alpine
```

Open http://localhost:8080 in your browser. You should see the Nginx welcome page.

Inspect the running container:

```bash
podman ps
podman port web-lab
podman logs web-lab
podman inspect web-lab
```

Stop, restart, and remove it:

```bash
podman stop web-lab
podman ps -a
podman start web-lab
podman stop web-lab
podman rm web-lab
```

If port 8080 is already occupied, change the mapping to `-p 8081:80` and open http://localhost:8081.

### Lab 1 deliverable

- Run `hello-world`.
- Run Nginx and open it in a browser.
- Inspect logs, ports, and container details.
- Stop and remove both test containers.

---

# Lab 2 — Important Podman Commands

## Objective

Practise the commands commonly used during container development and troubleshooting.

## Exercise 2.1 — Images

```bash
podman images
podman pull docker.io/library/python:3.12-slim
podman image inspect docker.io/library/python:3.12-slim
```

Remove the image only if no container depends on it and you no longer need it:

```bash
podman rmi docker.io/library/python:3.12-slim
```

If you remove it now, Podman will need to download it again in a later lab. It is fine to keep it.

## Exercise 2.2 — Run a temporary interactive container

```bash
podman run --rm -it docker.io/library/python:3.12-slim python --version
```

- `--rm`: remove the container after it exits.
- `-it`: allocate an interactive terminal.
- `python --version`: command executed inside the container.

## Exercise 2.3 — Container lifecycle

```bash
podman run -d --name command-lab -p 8082:80 docker.io/library/nginx:alpine
podman ps
podman logs command-lab
podman exec command-lab nginx -v
podman stop command-lab
podman start command-lab
podman restart command-lab
podman rm -f command-lab
```

`podman exec` runs a command inside an already running container. `podman rm -f` force-removes the container, stopping it first if necessary.

## Exercise 2.4 — Resource and system inspection

```bash
podman stats --no-stream
podman system df
podman info
podman machine list
```

`podman stats` shows resource usage for running containers. Some details vary by operating system and Podman version.

## Exercise 2.5 — Networks and volumes (optional exploration)

```bash
podman network ls
podman volume ls
podman volume create lab-data
podman volume inspect lab-data
podman volume rm lab-data
```

### Command reference

| Purpose | Command |
|---|---|
| Show running containers | `podman ps` |
| Show all containers | `podman ps -a` |
| Show images | `podman images` |
| Download an image | `podman pull IMAGE` |
| Start a container | `podman start NAME` |
| Stop a container | `podman stop NAME` |
| Restart a container | `podman restart NAME` |
| Remove a container | `podman rm NAME` |
| View logs | `podman logs NAME` |
| Execute a command in a container | `podman exec NAME COMMAND` |
| Inspect configuration | `podman inspect NAME` |
| View port mappings | `podman port NAME` |
| Build an image | `podman build -t NAME:TAG .` |
| View networks | `podman network ls` |
| View volumes | `podman volume ls` |
| View machine status | `podman machine list` |

### Lab 2 deliverable

Run the commands and explain the difference between an image and a container, and between `podman run`, `podman start`, and `podman exec`.

---

# Lab 3 — Containerize a FastAPI Inference API

## Objective

Create a small inference endpoint, build a container image, run it, and call the endpoint from the host machine.

The inference logic is deliberately lightweight and deterministic. It computes a logistic-regression-style probability from two numeric inputs. This demonstrates the API and deployment workflow without requiring a trained model file.

## Step 3.1 — Create the project structure

Create the following files:

```text
podman-inference-workshop/
├── app/
│   └── main.py
├── requirements.txt
└── Containerfile
```

Create the folders and files in your preferred editor.

## Step 3.2 — Create `app/main.py`

```python
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
```

## Step 3.3 — Create `requirements.txt`

```text
fastapi
uvicorn[standard]
redis
```

Redis is used in Lab 4. Installing it now keeps the same image usable for the Compose and Kubernetes labs.

## Step 3.4 — Create `Containerfile`

```dockerfile
FROM docker.io/library/python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

A `Containerfile` is compatible with the common Dockerfile syntax. It does not require Docker Desktop.

## Step 3.5 — Build the image

Run these commands from the `podman-inference-workshop` directory:

```bash
podman build -t localhost/inference-api:1.0 -f Containerfile .
podman images
```

The `localhost/` prefix identifies the image as a local image name.

## Step 3.6 — Run the API container

```bash
podman run -d --name inference-api -p 8000:8000 localhost/inference-api:1.0
```

Verify it:

```bash
podman ps
podman logs inference-api
```

Open the interactive API documentation:

http://localhost:8000/docs

## Step 3.7 — Test the inference endpoint

### Browser

Open http://localhost:8000/docs, select `POST /predict`, click **Try it out**, and submit:

```json
{
  "feature_1": 1.5,
  "feature_2": 0.5
}
```

### PowerShell (Windows)

```powershell
$body = @{
  feature_1 = 1.5
  feature_2 = 0.5
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri http://localhost:8000/predict `
  -ContentType "application/json" `
  -Body $body
```

### Terminal (macOS) or a shell with `curl`

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"feature_1":1.5,"feature_2":0.5}'
```

Expected response shape:

```json
{
  "probability": 0.759511,
  "prediction": 1,
  "model": "demo-logistic-score-v1"
}
```

The exact probability is determined by the formula in the code.

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

On Windows, you can also open `http://localhost:8000/health` in the browser.

## Step 3.8 — Clean up

```bash
podman stop inference-api
podman rm inference-api
```

Keep the built image; the next lab will reuse it.

### Lab 3 deliverable

A containerized FastAPI service with `/health`, `/predict`, and interactive `/docs` endpoints.

---

# Lab 4 — Multi-Container Application Using Compose

## Objective

Run the FastAPI inference API and Redis cache as two cooperating containers.

## Step 4.1 — Update `app/main.py`

Replace the contents of `app/main.py` with the following version. It adds optional Redis caching to the inference endpoint.

```python
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
```

This is a teaching example, not a production model-serving implementation. It uses Redis as a cache, not as a model store.

## Step 4.2 — Create `compose.yaml`

Create `compose.yaml` in the project root:

```yaml
services:
  api:
    build:
      context: .
      dockerfile: Containerfile
    image: localhost/inference-api:1.1
    environment:
      REDIS_URL: redis://redis:6379/0
    ports:
      - "8000:8000"
    depends_on:
      redis:
        condition: service_healthy

  redis:
    image: docker.io/library/redis:7-alpine
    command: ["redis-server", "--appendonly", "yes"]
    volumes:
      - redis-data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  redis-data:
```

Compose creates a private application network. The API connects to Redis by the Compose service name `redis`, not by `localhost`.

## Step 4.3 — Check Compose support

Podman's `podman compose` command is a wrapper around an external Compose provider. Check whether one is available:

```bash
podman compose version
```

If no provider is found, install a supported provider such as `podman-compose` or Docker Compose, then retry. See the official Podman Compose documentation:

https://docs.podman.io/en/stable/markdown/podman-compose.1.html

Podman Desktop may offer relevant setup guidance through its extensions or settings. Provider installation varies by OS and how Podman was installed.

## Step 4.4 — Build and start the application

From the project root:

```bash
podman compose up --build -d
```

Inspect the services:

```bash
podman compose ps
podman compose logs
podman compose logs api
podman compose logs redis
```

Test:

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

Submit the same `/predict` request twice. The first response should normally show `"cache": "miss"` and the second `"cache": "hit"`.

## Step 4.5 — Stop and clean up

Stop the application but retain the volume:

```bash
podman compose down
```

Stop the application and remove its Compose-managed volume:

```bash
podman compose down -v
```

The `-v` option deletes the Redis data volume. Use it only when you are comfortable losing the cached data.

### Lab 4 deliverable

A two-service application with FastAPI, Redis caching, service discovery, a health check, and persistent Redis storage.

---

# Lab 5 — Deploy to Kubernetes and Scale the API

## Objective

Create a local Kubernetes cluster through Podman Desktop, load the API image into it, deploy Redis and the API, expose the service, and scale the API replicas.

## Important concept

Podman runs containers; Kubernetes orchestrates Pods, Deployments, and Services. A local Kind cluster can run on a Podman-backed container engine. On Windows, Podman Desktop's Kind setup requires rootful Podman configuration. Consult the current official guide:

- https://podman-desktop.io/docs/kind
- https://podman-desktop.io/docs/kind/creating-a-kind-cluster

## Step 5.1 — Create a local Kind cluster in Podman Desktop

1. Open Podman Desktop.
2. Confirm that the Podman machine is running.
3. Open **Settings → Resources**.
4. Locate the **Kind** resource/extension.
5. If prompted, install the Kind CLI.
6. Create a new Kind cluster using the default configuration.
7. Wait until cluster creation completes.
8. Select the new `kind-...` Kubernetes context in Podman Desktop.

On Windows, follow Podman Desktop's instructions to configure Podman in rootful mode before creating the Kind cluster. On macOS, use the normal Podman machine configuration unless the current documentation indicates otherwise.

Verify from a terminal where `kubectl` is installed:

```bash
kubectl config current-context
kubectl get nodes
kubectl get pods -A
```

If `kubectl` is not installed, install it using the official instructions:
https://kubernetes.io/docs/tasks/tools/

## Step 5.2 — Build the Kubernetes version of the API image

The Compose lab used image tag `localhost/inference-api:1.1`. Kubernetes will use the same image, but the image must be available inside the Kind cluster.

From the project root:

```bash
podman build -t localhost/inference-api:1.1 -f Containerfile .
podman save -o inference-api-1.1.tar localhost/inference-api:1.1
```

Load the archive into the Kind cluster. Replace `podman-lab` with the actual Kind cluster name shown in Podman Desktop; if the cluster is named `podman-lab`, run:

```bash
kind load image-archive inference-api-1.1.tar --name podman-lab
```

Alternatively, use Podman Desktop's Images page: open the image's menu and choose **Push image to Kind cluster**, then select your cluster.

Confirm that the command targets the correct cluster. Kind image loading is cluster-specific.

## Step 5.3 — Create `k8s.yaml`

Create a `k8s` directory and place the following manifest in `k8s/k8s.yaml`, or save it as `k8s.yaml` in the project root.

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: inference-demo
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: inference-config
  namespace: inference-demo
data:
  REDIS_URL: redis://redis:6379/0
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: redis
  namespace: inference-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: redis
  template:
    metadata:
      labels:
        app: redis
    spec:
      containers:
        - name: redis
          image: docker.io/library/redis:7-alpine
          ports:
            - containerPort: 6379
          command: ["redis-server", "--appendonly", "yes"]
          readinessProbe:
            exec:
              command: ["redis-cli", "ping"]
            initialDelaySeconds: 3
            periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis
  namespace: inference-demo
spec:
  selector:
    app: redis
  ports:
    - port: 6379
      targetPort: 6379
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: inference-api
  namespace: inference-demo
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
        - name: api
          image: localhost/inference-api:1.1
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
          envFrom:
            - configMapRef:
                name: inference-config
          readinessProbe:
            httpGet:
              path: /ready
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 5
          livenessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 10
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: inference-api
  namespace: inference-demo
spec:
  selector:
    app: inference-api
  type: ClusterIP
  ports:
    - port: 8000
      targetPort: 8000
```

Notes:

- `Deployment` maintains the requested number of Pods.
- `Service` provides a stable endpoint for matching Pods.
- Redis is deployed once for this local exercise.
- `imagePullPolicy: Never` tells Kubernetes to use the image already loaded into the cluster.
- The API readiness probe checks Redis connectivity before marking a Pod ready.
- This single Redis instance is suitable for learning, not a highly available production setup.

## Step 5.4 — Deploy the application

From the directory containing `k8s.yaml`:

```bash
kubectl apply -f k8s.yaml
kubectl get all -n inference-demo
kubectl get pods -n inference-demo -w
```

Wait until the Redis Pod and both API Pods are ready. Press `Ctrl+C` to stop watching.

If a Pod does not start, inspect it:

```bash
kubectl describe pods -n inference-demo
kubectl logs deployment/inference-api -n inference-demo
kubectl logs deployment/redis -n inference-demo
```

## Step 5.5 — Access the API

Forward the Kubernetes Service to your local machine:

```bash
kubectl port-forward service/inference-api 8000:8000 -n inference-demo
```

Keep that terminal running. Open:

- API docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Readiness: http://localhost:8000/ready

Submit the same JSON used in Lab 3 to `POST /predict`.

## Step 5.6 — Scale the API

Scale from two to four replicas:

```bash
kubectl scale deployment/inference-api --replicas=4 -n inference-demo
kubectl get deployment inference-api -n inference-demo
kubectl get pods -n inference-demo -o wide
```

Wait for all four API Pods to become ready. Observe that Kubernetes creates additional Pods while the Service continues to route traffic to ready endpoints.

Scale down to one replica:

```bash
kubectl scale deployment/inference-api --replicas=1 -n inference-demo
kubectl get pods -n inference-demo
```

This is **manual replica scaling**. It demonstrates horizontal scaling by changing the number of application Pods. It does not automatically configure CPU-based autoscaling; that requires metrics and a Horizontal Pod Autoscaler configuration.

### Optional scaling exercise

Run the API call multiple times while changing the replica count. Inspect:

```bash
kubectl get endpoints inference-api -n inference-demo
kubectl describe service inference-api -n inference-demo
kubectl get deployment inference-api -n inference-demo
```

## Step 5.7 — Clean up Kubernetes resources

```bash
kubectl delete namespace inference-demo
```

This deletes the namespace and the resources created inside it.

To stop using the local cluster, delete it through Podman Desktop's Kind resource controls. If you created it using the Kind CLI, use the matching cluster name:

```bash
kind delete cluster --name podman-lab
```

Do not delete a cluster until you have confirmed its name and no longer need its workloads.

### Lab 5 deliverable

- Local Kubernetes cluster managed through Podman Desktop.
- FastAPI and Redis deployed as Kubernetes workloads.
- API exposed locally using `kubectl port-forward`.
- API scaled from two to four replicas and back down.
- Pods, Deployments, Services, readiness, and logs inspected.

---

# Troubleshooting Checklist

## API image is not found in Kubernetes

- Confirm the image name and tag match exactly: `localhost/inference-api:1.1`.
- Confirm that the image was loaded into the same Kind cluster selected in Podman Desktop.
- Confirm `imagePullPolicy: Never` is present in the API Deployment.
- Check `kubectl describe pod ...` for the exact error.

## API Pods are not ready

The `/ready` endpoint requires Redis to be available. Check Redis first:

```bash
kubectl get pods -n inference-demo
kubectl logs deployment/redis -n inference-demo
kubectl logs deployment/inference-api -n inference-demo
```

Check that `REDIS_URL` is `redis://redis:6379/0` and that the Redis Service exists.

## Compose command cannot find a provider

`podman compose` invokes an external provider. Install a supported Compose provider and check:

```bash
podman compose version
```

See https://docs.podman.io/en/stable/markdown/podman-compose.1.html

## Port 8000 is already in use

Stop the local container or process using port 8000. Alternatively, change the host-side port mapping in Compose to `"8001:8000"` and access the API at http://localhost:8001. For Kubernetes, use `kubectl port-forward service/inference-api 8001:8000 -n inference-demo`.

## Windows-specific Kind setup

Podman Desktop's Kind documentation states that Windows requires Podman to be configured in rootful mode for this workflow. Follow the current instructions at https://podman-desktop.io/docs/kind before creating the cluster.

---

# Final Workshop Summary

| Lab | Skills learned | Working result |
|---|---|---|
| 1 | Run, inspect, stop, and remove containers | Nginx container |
| 2 | Images, logs, exec, inspect, networks, volumes | Command practice |
| 3 | FastAPI, image build, port mapping, inference endpoint | Single API container |
| 4 | Compose, service discovery, Redis caching, volumes | API + Redis |
| 5 | Kubernetes Deployments, Services, probes, scaling | Scalable local API deployment |

## Official References

- Podman installation: https://podman.io/docs/installation
- Podman command documentation: https://docs.podman.io/
- Podman Compose: https://docs.podman.io/en/stable/markdown/podman-compose.1.html
- Podman Desktop Kind integration: https://podman-desktop.io/docs/kind
- Kind quick start: https://kind.sigs.k8s.io/docs/user/quick-start
- Kubernetes tools: https://kubernetes.io/docs/tasks/tools/

## Production note

This workshop is for local development and teaching. Before production use, replace the demonstration scoring function with a validated model artifact; pin dependency versions; configure resource requests and limits; manage secrets appropriately; add monitoring and structured logging; and design persistent, highly available data services as required.
