# FastAPI + Podman + Kind Kubernetes Workshop

A hands-on guide to build a FastAPI container image, deploy it to a local Kubernetes cluster created with Podman and Kind, verify the application, scale replicas, demonstrate self-healing, perform a rolling update, inspect logs, and clean up.

## Environment and assumptions

- Operating system: Windows, using **Command Prompt (CMD)**.
- Container engine: Podman.
- Kubernetes distribution: Kind running on Podman.
- Kubernetes context: `kind-ps-cluster`.
- Kind control-plane container: `ps-cluster-control-plane`.
- Application image: `localhost/inference-api:1.1`.
- FastAPI listens on port `8000`.
- Application source: `main.py`.
- The application exposes `/`, `/health`, `/ready`, and `/predict`.
- The `/predict` endpoint can compute a prediction if Redis is unavailable, but `/ready` requires Redis.

> **Important:** Run commands in the order shown. Commands labelled as being in a second terminal should be run in a separate CMD window. Keep the `kubectl port-forward` terminal open while testing the API.

---

## 1. Create the application files

Create this directory structure:

```text
workshop/
├── Containerfile
├── requirements.txt
└── main.py
```

Save your FastAPI application as `main.py`.

### `requirements.txt`

```text
fastapi
uvicorn[standard]
redis
```

### `Containerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

This Containerfile installs the dependencies, copies the application, and starts Uvicorn on port 8000.

## 2. Build and test the image locally

Run these commands from the directory containing `Containerfile`, `requirements.txt`, and `main.py`.

### Command 1 — Verify the files

```cmd
dir
```

**Purpose:** Confirm that the application source and build files are present.

### Command 2 — Build the image

```cmd
podman build -t localhost/inference-api:1.1 -f Containerfile .
```

**Purpose:** Build the FastAPI image and tag it as `localhost/inference-api:1.1`.

### Command 3 — Verify the image

```cmd
podman images localhost/inference-api
```

**Purpose:** Confirm that the image exists in Podman's local image store.

### Command 4 — Run a temporary local container

```cmd
podman run -d --name inference-test -p 8000:8000 localhost/inference-api:1.1
```

**Purpose:** Start the API locally to test the image before deploying it to Kubernetes.

### Command 5 — Test the health endpoint

```cmd
curl.exe http://localhost:8000/health
```

**Purpose:** Verify that FastAPI responds. Expected response: `{"status":"ok"}`.

### Command 6 — Test prediction

```cmd
curl.exe -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"feature_1\":2.5,\"feature_2\":1.2}"
```

**Purpose:** Send sample features and verify that the inference endpoint returns a prediction.

### Command 7 — Stop and remove the temporary container

```cmd
podman rm -f inference-test
```

**Purpose:** Free port 8000 and remove the local test container before port forwarding later.

> If port 8000 is already occupied, use a different host port such as `8001:8000` for the temporary test.

## 3. Check and select the Kubernetes cluster

### Command 8 — Select the Kind Podman provider

```cmd
set KIND_EXPERIMENTAL_PROVIDER=podman
```

**Purpose:** Tell Kind to use Podman for the current CMD session.

### Command 9 — Select the Kubernetes context

```cmd
kubectl config use-context kind-ps-cluster
```

**Purpose:** Direct `kubectl` commands to the intended cluster.

### Command 10 — Verify the active context

```cmd
kubectl config current-context
```

**Purpose:** Confirm that the selected context is `kind-ps-cluster`.

### Command 11 — Check cluster nodes

```cmd
kubectl get nodes
```

**Purpose:** Verify that the control-plane node is present and `Ready`.

### Command 12 — Check system Pods

```cmd
kubectl get pods -A
```

**Purpose:** Inspect Pods across all namespaces and confirm that Kubernetes components are running.

## 4. Transfer the image into the Kind cluster

Podman's image store and the containerd image store inside the Kind node are separate. The image must be imported into the node so Kubernetes can start it without pulling it from a registry.

### Command 13 — Save the image to an archive

```cmd
podman save -o inference-api.tar localhost/inference-api:1.1
```

**Purpose:** Export the local Podman image to a tar archive.

### Command 14 — Copy the archive into the Kind control-plane container

```cmd
podman cp inference-api.tar ps-cluster-control-plane:/tmp/inference-api.tar
```

**Purpose:** Transfer the archive into the Kind node container.

### Command 15 — Import the image into containerd

```cmd
podman exec --privileged ps-cluster-control-plane ctr --namespace=k8s.io images import /tmp/inference-api.tar
```

**Purpose:** Make the image available in containerd's Kubernetes image namespace.

### Command 16 — Verify the imported image

```cmd
podman exec ps-cluster-control-plane ctr --namespace=k8s.io images ls
```

**Purpose:** Confirm that `localhost/inference-api:1.1` appears in the node's image list.

> If the control-plane container name differs, check `podman ps -a` and replace `ps-cluster-control-plane` with the actual name. If image import fails, resolve that error before creating the Deployment.

## 5. Deploy FastAPI to Kubernetes

### Command 17 — Create a Deployment with two replicas

```cmd
kubectl create deployment inference-api --image=localhost/inference-api:1.1 --replicas=2
```

**Purpose:** Ask Kubernetes to maintain two application Pods.

### Command 18 — Set the image pull policy

```cmd
kubectl patch deployment inference-api -p "{\"spec\":{\"template\":{\"spec\":{\"containers\":[{\"name\":\"inference-api\",\"imagePullPolicy\":\"IfNotPresent\"}]}}}}"
```

**Purpose:** Allow Kubernetes to use the image already imported into the node rather than requiring a registry pull.

### Command 19 — Wait for the rollout

```cmd
kubectl rollout status deployment/inference-api --timeout=120s
```

**Purpose:** Wait for the Deployment to finish creating its replicas. If this fails, inspect `kubectl get pods` and `kubectl describe pod <POD_NAME>`.

### Command 20 — Expose the Deployment as a Service

```cmd
kubectl expose deployment inference-api --name=inference-api --port=8000 --target-port=8000
```

**Purpose:** Create a ClusterIP Service that routes port 8000 to the application containers on port 8000.

### Command 21 — Inspect Deployment, Pods, and Service

```cmd
kubectl get deployments,pods,services
```

**Purpose:** Verify that the Deployment, two Pods, and Service exist.

### Command 22 — Inspect Pod placement and IP addresses

```cmd
kubectl get pods -o wide
```

**Purpose:** Show Pod status, node placement, and IP addresses.

> **Redis note:** The provided FastAPI code uses Redis at `redis://localhost:6379/0` by default. In Kubernetes, `localhost` inside an API Pod refers to that same Pod, not a separate Redis Pod. If you want `/ready` and cache hit/miss behavior to work in Kubernetes, deploy Redis as a separate Service and set `REDIS_URL` to a service address such as `redis://redis:6379/0`. The health and prediction endpoints can still work without Redis because prediction falls back to uncached inference.

## 6. Access and test the application

### Command 23 — Start port forwarding (Terminal 1)

```cmd
kubectl port-forward service/inference-api 8000:8000
```

**Purpose:** Forward local port 8000 to the Kubernetes Service. Keep this terminal open.

Open a **second CMD terminal** for Commands 24–26.

### Command 24 — Test health (Terminal 2)

```cmd
curl.exe http://localhost:8000/health
```

**Purpose:** Verify that requests reach the deployed FastAPI application. Expected response: `{"status":"ok"}`.

### Command 25 — Test the application root (Terminal 2)

```cmd
curl.exe http://localhost:8000/
```

**Purpose:** Verify the root endpoint returns the API message and documentation path.

### Command 26 — Test inference (Terminal 2)

```cmd
curl.exe -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d "{\"feature_1\":2.5,\"feature_2\":1.2}"
```

**Purpose:** Submit sample features and verify the prediction response.

## 7. Demonstrate scaling

### Command 27 — Scale to four replicas

```cmd
kubectl scale deployment/inference-api --replicas=4
```

**Purpose:** Increase the desired number of application Pods from two to four.

### Command 28 — Watch Pods (optional)

```cmd
kubectl get pods -w
```

**Purpose:** Observe Kubernetes create the additional Pods. Press `Ctrl+C` to stop watching.

### Command 29 — Verify replica counts

```cmd
kubectl get deployment inference-api
```

**Purpose:** Confirm that desired and available replicas reach four.

### Command 30 — Inspect all application Pods

```cmd
kubectl get pods -o wide
```

**Purpose:** Confirm that four application Pods are present and inspect their status.

### Command 31 — Inspect Deployment details

```cmd
kubectl describe deployment inference-api
```

**Purpose:** Review replica status, the selector, rollout information, and recent events.

## 8. Demonstrate self-healing

### Command 32 — List Pods to choose one

```cmd
kubectl get pods
```

**Purpose:** Copy the name of one `inference-api` Pod.

### Command 33 — Delete one application Pod

Replace `POD_NAME` with an actual Pod name, without angle brackets:

```cmd
kubectl delete pod POD_NAME
```

**Purpose:** Simulate a Pod failure. The Deployment's ReplicaSet should create a replacement.

### Command 34 — Watch Kubernetes replace it

```cmd
kubectl get pods -w
```

**Purpose:** Observe the replacement Pod being created and becoming ready. Press `Ctrl+C` to stop watching.

## 9. Demonstrate rolling updates and rollback

This section builds version `1.2` from the current source, transfers it into Kind, and updates the Deployment. For a meaningful application update, modify the source or another build input before building version `1.2`; otherwise the new image may be functionally identical to version `1.1`.

### Command 35 — Build version 1.2

```cmd
podman build -t localhost/inference-api:1.2 -f Containerfile .
```

**Purpose:** Build a new image version.

### Command 36 — Export version 1.2

```cmd
podman save -o inference-api-1.2.tar localhost/inference-api:1.2
```

**Purpose:** Create an archive of the new image.

### Command 37 — Copy the archive into the Kind node

```cmd
podman cp inference-api-1.2.tar ps-cluster-control-plane:/tmp/inference-api-1.2.tar
```

**Purpose:** Transfer the new image archive into the control-plane container.

### Command 38 — Import version 1.2 into containerd

```cmd
podman exec --privileged ps-cluster-control-plane ctr --namespace=k8s.io images import /tmp/inference-api-1.2.tar
```

**Purpose:** Make version 1.2 available to Kubernetes.

### Command 39 — Update the Deployment image

```cmd
kubectl set image deployment/inference-api inference-api=localhost/inference-api:1.2
```

**Purpose:** Trigger a rolling update to the new image.

### Command 40 — Monitor the rollout

```cmd
kubectl rollout status deployment/inference-api --timeout=120s
```

**Purpose:** Wait for the new ReplicaSet to roll out.

### Command 41 — Roll back if needed

```cmd
kubectl rollout undo deployment/inference-api
```

**Purpose:** Restore the previous Deployment revision.

### Command 42 — Inspect rollout history

```cmd
kubectl rollout history deployment/inference-api
```

**Purpose:** Review the recorded Deployment revisions.

## 10. Logs, events, and cleanup

### Command 43 — View application logs

```cmd
kubectl logs deployment/inference-api --all-pods=true
```

**Purpose:** Inspect application logs from the Deployment's Pods.

### Command 44 — Inspect recent cluster events

```cmd
kubectl get events --sort-by=.metadata.creationTimestamp
```

**Purpose:** Review recent scheduling, scaling, and troubleshooting events.

### Command 45 — Delete the Service

```cmd
kubectl delete service inference-api
```

**Purpose:** Remove the Service endpoint.

### Command 46 — Delete the Deployment

```cmd
kubectl delete deployment inference-api
```

**Purpose:** Remove the Deployment and its managed Pods.

### Command 47 — Verify cleanup

```cmd
kubectl get deployments,pods,services
```

**Purpose:** Confirm that the application resources have been removed. Other unrelated resources may remain.

### Command 48 — Remove image archive files

```cmd
del inference-api.tar
del inference-api-1.2.tar
```

**Purpose:** Delete the local transfer archives. This does not delete the image from Podman or from the Kind node.

---

## What this workshop demonstrates

| Feature | Commands |
|---|---:|
| Build and test a container image | 1–7 |
| Check Kubernetes and select a context | 8–12 |
| Transfer image into Kind | 13–16 |
| Deploy and expose an application | 17–22 |
| Access and test the API | 23–26 |
| Scale replicas | 27–31 |
| Self-healing | 32–34 |
| Rolling updates and rollback | 35–42 |
| Logs, events, and cleanup | 43–48 |

## Troubleshooting quick reference

```cmd
kubectl config current-context
kubectl get nodes
kubectl get pods -o wide
kubectl describe pod POD_NAME
kubectl logs POD_NAME
kubectl get events --sort-by=.metadata.creationTimestamp
podman ps -a
```

- **Pod stuck in `ImagePullBackOff` or `ErrImagePull`:** Verify the image is imported into the Kind node's containerd image store and that the Deployment's image name matches.
- **Pod stuck in `CrashLoopBackOff`:** Inspect `kubectl logs POD_NAME` and `kubectl describe pod POD_NAME`.
- **API unavailable:** Check Pod readiness, the Service, the port-forward terminal, and whether the app listens on `0.0.0.0:8000`.
- **Redis readiness fails:** Deploy Redis and configure `REDIS_URL` to point to the Redis Kubernetes Service.
