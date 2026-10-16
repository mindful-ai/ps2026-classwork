# Podman Installation Guide: Windows 11 and macOS (Apple Silicon M5)

This guide covers installing Podman, creating its Linux environment, verifying the installation, and running a test container on Windows 11 and Apple Silicon Macs, including M5-based MacBook Air and MacBook Pro systems.

## 1. Overview

Podman is an open-source container engine. Because Linux containers require a Linux kernel:

- **Windows 11:** Podman typically runs containers in a Podman machine backed by WSL 2.
- **macOS (M5 / Apple Silicon):** Podman runs containers in a lightweight Linux virtual machine.

You can use Podman from the command line. Podman Desktop is optional and provides a graphical interface.

## 2. Install Podman on Windows 11

### Step 1 — Check prerequisites

- Windows 11, preferably fully updated.
- Administrator access for initial setup.
- Hardware virtualization enabled in BIOS/UEFI.
- WSL 2 installed and working.

### Step 2 — Install or update WSL 2

Open **PowerShell as Administrator** and run:

```powershell
wsl --install
wsl --update
wsl --status
```

Restart Windows if prompted. If WSL is already installed, use the update and status commands to check it.

### Step 3 — Install Podman

Use the official resources:

- [Podman installation documentation](https://podman.io/docs/installation)
- [Podman Desktop](https://podman-desktop.io/)

Choose one of the following:

- **Podman CLI:** suitable for terminal-based work.
- **Podman Desktop:** adds a graphical interface for managing containers and images.

Follow the installer prompts. Reopen PowerShell or your terminal after installation.

### Step 4 — Initialize and start the Podman machine

In PowerShell, run:

```powershell
podman --version
podman machine list
```

If no machine exists, create one:

```powershell
podman machine init
```

Start it and verify the engine:

```powershell
podman machine start
podman info
```

If Podman Desktop or the installer has already created a machine, use `podman machine list` and start the existing machine rather than creating another one.

## 3. Install Podman on macOS (M5 / Apple Silicon)

### Step 1 — Verify the architecture

Open **Terminal** and run:

```bash
uname -m
sw_vers
```

On Apple Silicon, `uname -m` should normally return `arm64`.

### Step 2 — Install Podman

Choose one installation method.

**Option A — Homebrew**

If Homebrew is already installed:

```bash
brew install podman
```

**Option B — Official installer**

Follow the current macOS instructions on:

- [Podman installation documentation](https://podman.io/docs/installation)
- [Podman releases](https://github.com/containers/podman/releases)

Use an installer compatible with macOS and Apple Silicon.

### Step 3 — Initialize and start the Podman machine

In Terminal, run:

```bash
podman --version
podman machine list
```

If no machine exists, create one:

```bash
podman machine init
```

Start it and verify the engine:

```bash
podman machine start
podman info
```

The machine provides the Linux environment required to run Linux containers on macOS. If a machine already exists, start it rather than creating another one.

### Step 4 — Optional: install Podman Desktop

Download [Podman Desktop](https://podman-desktop.io/). Open it and follow the onboarding instructions to configure Podman. Create a Podman machine if one does not already exist.

## 4. Run Your First Container (Windows and macOS)

After the Podman machine is running, these commands work in PowerShell or Terminal.

### Test with `hello-world`

```bash
podman run --name hello-podman hello-world
podman ps -a
podman rm hello-podman
```

The output should confirm that the container ran successfully.

### Run a web server

```bash
podman run -d --name web-demo -p 8080:80 docker.io/library/nginx:alpine
```

Open this URL in a browser:

<http://localhost:8080>

You should see the Nginx welcome page.

Stop and remove the container when finished:

```bash
podman stop web-demo
podman rm web-demo
```

If port 8080 is already in use, use `-p 8081:80` and visit <http://localhost:8081>.

## 5. Essential Podman Commands

| Task | Command |
|---|---|
| Check Podman version | `podman --version` |
| Show machine status | `podman machine list` |
| Start the machine | `podman machine start` |
| Stop the machine | `podman machine stop` |
| Show engine information | `podman info` |
| List images | `podman images` |
| List running containers | `podman ps` |
| List all containers | `podman ps -a` |
| View container logs | `podman logs web-demo` |
| Stop a container | `podman stop web-demo` |
| Remove a container | `podman rm web-demo` |

## 6. Common Problems

### `podman` is not recognized (Windows)

- Reopen PowerShell after installation.
- Check that Podman is installed and its executable directory is on `PATH`.

### Podman machine fails to start (Windows)

- Confirm that WSL 2 is installed and updated.
- Check that hardware virtualization is enabled.
- Restart Windows if a system update or WSL installation requested it.
- Inspect the machine with `podman machine list`.

### Podman machine fails to start (macOS)

- Confirm that Podman installation completed successfully.
- Run `podman machine list` to inspect existing machines.
- Start an existing machine before attempting to initialize another one.

### Port is already in use

Change the host port, for example:

```bash
podman run -d --name web-demo -p 8081:80 docker.io/library/nginx:alpine
```

Then open <http://localhost:8081>.

## 7. Does Podman Include Kubernetes?

**No.** Installing Podman does not install a complete Kubernetes cluster by default.

- **Podman:** builds and runs containers.
- **Podman Desktop:** provides a GUI and can integrate with Kubernetes tools and clusters.
- **Kind or Minikube:** creates a local Kubernetes cluster for learning and testing.

For a learning environment, install Podman first. Add Kind or Minikube when you are ready to practise Kubernetes.

Useful links:

- [Podman](https://podman.io/)
- [Podman Desktop](https://podman-desktop.io/)
- [Kind](https://kind.sigs.k8s.io/)
- [Minikube](https://minikube.sigs.k8s.io/)

## 8. Recommended Setup for Development Workshops

For Python, FastAPI, Streamlit, and AI application projects:

1. Install Podman CLI.
2. Confirm the Podman machine starts successfully.
3. Practise pulling images and running containers.
4. Learn to build images with a Dockerfile-compatible workflow.
5. Add Podman Desktop if a graphical interface is useful.
6. Install Kind or Minikube separately when you begin Kubernetes exercises.

## Official References

- [Podman installation documentation](https://podman.io/docs/installation)
- [Podman for Windows guide](https://github.com/containers/podman/blob/main/docs/tutorials/podman-for-windows.md)
- [Podman Desktop installation for macOS](https://podman-desktop.io/docs/installation/macos-install)
