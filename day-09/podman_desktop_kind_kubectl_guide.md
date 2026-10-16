# Using Podman Desktop, Kind, and kubectl

## 1. How Podman Desktop, Kind, and kubectl work together

These tools have different responsibilities:

- **Podman Desktop:** A graphical interface for containers, Podman machines, and supported Kubernetes integrations. It can help you create and inspect a local cluster.
- **Podman machine / container engine:** Provides the environment in which containers run.
- **Kind:** Creates a local Kubernetes cluster using containers as Kubernetes nodes.
- **kubectl:** Connects to an existing Kubernetes cluster to deploy and manage Kubernetes resources.

Conceptually:

```text
Podman Desktop
      |
      v
Podman machine / container engine
      |
      v
Kind Kubernetes cluster
      |
      v
kubectl
  - deploy applications
  - inspect Pods and Deployments
  - manage Services
  - view logs
  - scale workloads
```

Podman Desktop can integrate with Kind and help create or inspect clusters. You can also create a Kind cluster through the Kind CLI.

## 2. Can you avoid running the `kind` command manually?

**Yes, if you create the cluster through Podman Desktop's graphical interface.**

However, a Kubernetes cluster must still be created by some method. `kubectl` alone does not create a Kubernetes cluster; it communicates with an existing cluster using the selected Kubernetes context.

Once the cluster exists, you can use `kubectl` for the application deployment and management exercises.

## 3. Verify Kubernetes access

After creating the cluster through Podman Desktop, open PowerShell on Windows or Terminal on macOS and run:

```bash
kubectl config get-contexts
kubectl config current-context
kubectl get nodes
```

Check that the current context points to the cluster you created and that its nodes are ready.

If `kubectl` is not installed, follow the official instructions:
https://kubernetes.io/docs/tasks/tools/

## 4. Deploy the application with kubectl

From the directory containing the Kubernetes manifest `k8s.yaml`, run:

```bash
kubectl apply -f k8s.yaml
kubectl get pods -n inference-demo
kubectl get deployments -n inference-demo
kubectl get services -n inference-demo
```

Wait until the Redis Pod and the FastAPI Pods are ready.

### Inspect a problem

```bash
kubectl describe pods -n inference-demo
kubectl logs deployment/inference-api -n inference-demo
kubectl logs deployment/redis -n inference-demo
```

These commands help identify image, startup, readiness, and connectivity issues.

## 5. Scale the FastAPI application

Scale the Deployment to four replicas:

```bash
kubectl scale deployment/inference-api --replicas=4 -n inference-demo
kubectl get pods -n inference-demo -w
```

Wait for the Pods to become ready, then press `Ctrl+C` to stop watching.

Scale down to one replica:

```bash
kubectl scale deployment/inference-api --replicas=1 -n inference-demo
kubectl get deployments -n inference-demo
kubectl get pods -n inference-demo
```

Kubernetes maintains the requested number of API Pods. This is manual replica scaling; automatic CPU-based scaling requires additional metrics and a Horizontal Pod Autoscaler configuration.

## 6. Access the FastAPI application

Run this command and leave the terminal open:

```bash
kubectl port-forward service/inference-api 8000:8000 -n inference-demo
```

Open the interactive API documentation:

http://localhost:8000/docs

You can also test:

- Health endpoint: http://localhost:8000/health
- Readiness endpoint: http://localhost:8000/ready

## 7. Delete the application resources

When you finish the exercise:

```bash
kubectl delete namespace inference-demo
```

This deletes the namespace and the Kubernetes resources inside it. It does not necessarily delete the Kind cluster itself.

If you also want to delete the local cluster, use Podman Desktop's cluster controls. If you created the cluster with the Kind CLI, you can delete it with the matching cluster name:

```bash
kind delete cluster --name podman-lab
```

Only use the example name `podman-lab` if that is the actual name of your cluster.

## 8. Recommended workflow for the workshop

| Task | Recommended tool |
|---|---|
| Build images and run containers | Podman CLI |
| Inspect containers visually | Podman Desktop |
| Create a local Kubernetes cluster | Podman Desktop |
| Deploy Kubernetes YAML | `kubectl apply` |
| Inspect Pods and Services | `kubectl get`, `kubectl describe` |
| View application logs | `kubectl logs` |
| Scale the application | `kubectl scale` |
| Access the API locally | `kubectl port-forward` |
| Delete application resources | `kubectl delete` |

### Important: make the image available to the cluster

The FastAPI image must be available inside the Kind cluster before its Pods can start. You can use Podman Desktop's image-loading integration or the appropriate Kind image-loading procedure. This is separate from applying the Kubernetes manifest with `kubectl`.

For the tutorial image `localhost/inference-api:1.1`, ensure the image has been loaded into the same Kind cluster that your `kubectl` context targets. If the Deployment uses `imagePullPolicy: Never`, Kubernetes will only use an image already present in the cluster.

On Windows, follow Podman Desktop's current Kind setup instructions, including its rootful Podman requirements where applicable:
https://podman-desktop.io/docs/kind

## 9. Official references

- [Podman Desktop](https://podman-desktop.io/)
- [Podman Desktop: Kind integration](https://podman-desktop.io/docs/kind)
- [Kind quick start](https://kind.sigs.k8s.io/docs/user/quick-start)
- [kubectl installation](https://kubernetes.io/docs/tasks/tools/)
- [kubectl command reference](https://kubernetes.io/docs/reference/kubectl/)

## Summary

You can create the Kubernetes cluster through Podman Desktop and use `kubectl` for deploying, inspecting, scaling, accessing, and deleting application resources. Kind is the cluster-creation mechanism in this workflow; it is not a replacement for `kubectl`.
