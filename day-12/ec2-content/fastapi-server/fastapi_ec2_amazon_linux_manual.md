# FastAPI Deployment on AWS EC2 (Amazon Linux 2023)

A hands-on manual for cloning a FastAPI project from Git, installing dependencies, launching the server, testing endpoints, and troubleshooting common issues.

## 1. Overview

This manual assumes:

- An EC2 instance running **Amazon Linux 2023**
- You can connect to the instance using SSH
- Your FastAPI project is stored in a Git repository
- The example application listens on port `8000`

Replace placeholders such as `USERNAME`, `REPOSITORY`, and `<EC2-Public-IP>` with your actual values.

## 2. Connect to EC2

From your local terminal, connect using the correct key and username:

```bash
ssh -i "my-key.pem" ec2-user@<EC2-Public-IP>
```

Once connected, confirm the operating system:

```bash
cat /etc/os-release
```

## 3. Update packages and install Git and Python

Update package metadata and install the required tools:

```bash
sudo dnf update -y
sudo dnf install -y git python3 python3-pip
```

Verify the installations:

```bash
git --version
python3 --version
python3 -m pip --version
```

### If Git is unavailable

Try:

```bash
sudo dnf clean all
sudo dnf makecache
sudo dnf install -y git
git --version
```

If the install fails, inspect the exact error and test connectivity:

```bash
curl -I https://github.com
```

If the instance has no outbound internet access, check its subnet route table, NAT gateway or public IPv4 connectivity, security controls, and DNS configuration. A public IP alone does not guarantee working outbound access.

## 4. Clone the Git repository

For a public HTTPS repository:

```bash
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
```

Check the files:

```bash
pwd
ls -la
```

For a private repository, configure an approved authentication method. Do not paste access tokens into shell commands that may be saved in shell history. If your project uses Git submodules, clone with:

```bash
git clone --recurse-submodules https://github.com/USERNAME/REPOSITORY.git
```

If the project is already cloned and you want to pull the latest changes:

```bash
git pull
```

Run `git pull` from the intended repository directory and branch.

## 5. Identify the application entry point

Look for files such as:

```bash
ls
find . -maxdepth 3 -type f \( -name "main.py" -o -name "app.py" -o -name "requirements.txt" -o -name "pyproject.toml" \)
```

Typical Uvicorn targets:

| Project layout | Uvicorn target |
|---|---|
| `main.py` contains `app = FastAPI()` | `main:app` |
| `app.py` contains `app = FastAPI()` | `app:app` |
| `app/main.py` contains `app = FastAPI()` | `app.main:app` |
| `src/api.py` contains `app = FastAPI()` | Depends on Python import path; commonly `src.api:app` |

The part before `:` is the Python module path. The part after `:` is the FastAPI variable name.

## 6. Create and activate a virtual environment

From the project root:

```bash
python3 -m venv venv
source venv/bin/activate
```

Your shell prompt should normally show `(venv)`.

Upgrade pip:

```bash
python -m pip install --upgrade pip
```

When returning to the project later, activate the environment again:

```bash
cd REPOSITORY
source venv/bin/activate
```

## 7. Install Python dependencies

### Option A: The repository has `requirements.txt`

```bash
pip install -r requirements.txt
```

### Option B: No dependency file exists

For a minimal FastAPI application:

```bash
pip install fastapi "uvicorn[standard]"
```

### Option C: The repository uses `pyproject.toml`

Read the project's README and `pyproject.toml` for its intended installation command. For projects configured as installable packages, this may be:

```bash
pip install .
```

Do not install only FastAPI and Uvicorn if the application requires additional libraries, such as database drivers or ML packages.

Confirm the imports:

```bash
python -c "import fastapi, uvicorn; print('FastAPI and Uvicorn installed')"
```

## 8. Create a minimal FastAPI application (optional)

If you do not already have an application, create `main.py`:

```bash
cat > main.py <<'PY'
from fastapi import FastAPI

app = FastAPI(title="EC2 FastAPI Demo")

@app.get("/")
def home():
    return {"message": "Hello from FastAPI on AWS EC2"}

@app.get("/health")
def health():
    return {"status": "ok"}
PY
```

This creates a basic application with a home route and health-check route.

## 9. Launch the FastAPI server

Run this from the directory containing `main.py`, with the virtual environment activated:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

Explanation:

- `main` is the filename `main.py`, without `.py`.
- `app` is the FastAPI object defined in that file.
- `--host 0.0.0.0` listens on the instance network interfaces.
- `--port 8000` selects port 8000.

For development only, automatic reload is available:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Do not use `--reload` for a production deployment.

Keep the terminal open while testing. Press `Ctrl+C` to stop a foreground server.

## 10. Test the API from EC2

Open another SSH session, or stop the server and restart it in the background later. While the server is running, test locally:

```bash
curl http://127.0.0.1:8000/
curl http://127.0.0.1:8000/health
```

Expected responses:

```json
{"message":"Hello from FastAPI on AWS EC2"}
```

```json
{"status":"ok"}
```

Check the API documentation endpoint:

```bash
curl -I http://127.0.0.1:8000/docs
```

## 11. Allow inbound traffic in the EC2 security group

To access the API from your own computer:

1. Open **AWS Console → EC2 → Instances**.
2. Select the instance.
3. Open its **Security** tab and select the attached security group.
4. Choose **Edit inbound rules**.
5. Add the following rule for a temporary demo:

| Setting | Value |
|---|---|
| Type | Custom TCP |
| Port | `8000` |
| Source | My IP |

Save the rule.

Use the narrowest source range practical. Avoid `0.0.0.0/0` for a development API unless public access is intentionally required and appropriately secured. A security group rule is not sufficient if the instance has no working route from the internet.

## 12. Access the API from your browser

Replace `<EC2-Public-IP>` with the instance's public IPv4 address:

- API root: `http://<EC2-Public-IP>:8000/`
- Health check: `http://<EC2-Public-IP>:8000/health`
- Interactive Swagger UI: `http://<EC2-Public-IP>:8000/docs`
- OpenAPI schema: `http://<EC2-Public-IP>:8000/openapi.json`

If the instance has no public IP, use an appropriate private network, VPN, bastion, or managed access method instead of expecting these public URLs to work.

## 13. Run the server in the background (quick demo)

For a quick test, stop any foreground server with `Ctrl+C`, then run:

```bash
nohup ./venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 > fastapi.log 2>&1 &
```

If your virtual environment is named differently, adjust the path. If the entry point is not `main:app`, use the correct target.

Inspect the process and logs:

```bash
pgrep -af uvicorn
tail -n 50 fastapi.log
```

Follow the log live:

```bash
tail -f fastapi.log
```

Stop the process:

```bash
pgrep -af uvicorn
kill <PID>
```

Replace `<PID>` with the actual process ID. Do not kill a process until you have verified that it is the intended server.

`nohup` is suitable for a quick demo, but it is not a robust production service manager and will not automatically restart the app after every failure or reboot.

## 14. Check whether the server is listening

On EC2:

```bash
sudo ss -lntp | grep ':8000'
```

Check the service response locally:

```bash
curl -v http://127.0.0.1:8000/health
```

If the local request works but an external request fails, inspect the EC2 security group, network ACL, subnet route table, public IP, and any host firewall configuration.

## 15. Update the application from Git

From the repository directory:

```bash
git status
git pull
source venv/bin/activate
pip install -r requirements.txt
```

If dependencies changed, reinstall them before restarting the application. A server launched manually or using `nohup` must be stopped and started again to load code changes. For production, use a service manager and a controlled deployment procedure.

## 16. Common errors and fixes

### `git: command not found`

```bash
sudo dnf install -y git
git --version
```

If that fails, inspect the package manager error and confirm the instance can reach package repositories.

### `python3 -m venv venv` fails

Check the Python installation and the exact error:

```bash
python3 --version
python3 -m venv venv
```

Install the appropriate Python package available for your Amazon Linux release if required.

### `ModuleNotFoundError`

Activate the virtual environment and install the project's dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Verify that Uvicorn is using the same Python environment:

```bash
which python
which uvicorn
```

### `Could not import module "main"`

Confirm your current directory and files:

```bash
pwd
ls -la
```

Ensure `main.py` exists and defines `app = FastAPI()`. Adjust the Uvicorn target if the file or variable has a different name.

### `Address already in use`

Another process may already be using port 8000:

```bash
sudo ss -lntp | grep ':8000'
pgrep -af uvicorn
```

Stop the intended old process or choose another port.

### Browser times out, but local curl works

Check:

- Inbound security group rule for TCP port 8000
- Correct public IPv4 address
- Internet gateway and subnet route for a public instance
- Network ACLs and host firewall rules
- Whether Uvicorn is bound to `0.0.0.0`, not just `127.0.0.1`

### `Permission denied (publickey)` when cloning

This is a Git authentication issue, not an EC2 SSH issue. For a private repository, configure an approved Git credential or deploy-key method. Never share private keys or tokens.

## 17. Production deployment notes

The direct Uvicorn command and `nohup` method are for learning and demos. Before exposing a real application publicly:

- Put it behind a reverse proxy or load balancer and use HTTPS.
- Keep application secrets in a suitable secrets manager or environment configuration; do not commit them to Git.
- Restrict inbound ports and allow only the traffic needed.
- Run the application under a dedicated, least-privileged service account where practical.
- Configure process supervision, logs, monitoring, health checks, and restart behavior.
- Pin and review dependencies.
- Do not run development reload mode in production.
- Consider AWS Systems Manager Session Manager to reduce the need for public SSH access.

## 18. Quick-start command summary

Use these commands after replacing the repository URL and project directory:

```bash
sudo dnf install -y git python3 python3-pip
git clone https://github.com/USERNAME/REPOSITORY.git
cd REPOSITORY
python3 -m venv venv
source venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

If there is no `requirements.txt`, install the project's documented dependencies; for a minimal app, use:

```bash
pip install fastapi "uvicorn[standard]"
```

Remember to configure inbound TCP port `8000` in the EC2 security group if you need to access the API externally.
