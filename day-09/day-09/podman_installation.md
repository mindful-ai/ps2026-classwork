# Does Podman Installation Include Kubernetes?

**No.** Installing Podman does not include a complete Kubernetes cluster by default.

## What Each Tool Does

- **Podman:** Builds and runs containers.
- **Podman Desktop:** Provides a graphical interface and can integrate with Kubernetes tools and clusters.
- **Kind / Minikube:** Creates a local Kubernetes cluster for learning and testing.

## Recommendation

Install Podman first. When you are ready to learn Kubernetes, install **Kind** or **Minikube** to create a local cluster.

## Useful Links

- [Podman](https://podman.io/)
- [Podman Desktop](https://podman-desktop.io/)
- [Kind](https://kind.sigs.k8s.io/)
- [Minikube](https://minikube.sigs.k8s.io/)
