# Beginner-Friendly Manual: GitHub Actions, EC2, and Port Configuration

## Project overview

This manual explains how GitHub Actions tests a FastAPI project, builds
and publishes a Podman container image to GitHub Container Registry
(GHCR), and how to run that image on Amazon EC2.

The example project is `fastapi-podman-crud`. Its endpoints include `/`,
`/health`, `/docs`, and CRUD endpoints under `/products`.

> **Important:** The starter API stores products in memory. Its data is
> lost when the application process restarts. Use a database for
> persistent data in production.

# Part 1 --- GitHub Actions: Beginner Guide

## 1. What is GitHub Actions?

GitHub Actions automatically runs tasks when events occur in your
repository. In this project:

1.  You push code to GitHub or open a pull request.
2.  GitHub Actions installs Python dependencies.
3.  It runs automated tests.
4.  On a push to `main`, after tests pass, it installs Podman and builds
    a container image.
5.  It starts a temporary container and checks `/health`.
6.  It publishes the image to GHCR.

**This workflow builds and publishes the image. It does not
automatically deploy to EC2.**

## 2. Workflow file location

Create this file in the repository:

``` text
.github/workflows/ci-cd.yml
```

## 3. Workflow YAML

Save the following content in `.github/workflows/ci-cd.yml`:

``` yaml
name: FastAPI CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: pip install -r requirements-dev.txt

      - name: Run tests
        run: pytest -v

  build:
    needs: test
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest

    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Install Podman
        run: sudo apt-get update && sudo apt-get install -y podman

      - name: Build image
        run: |
          IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}
          podman build -t $IMAGE:$GITHUB_SHA .

      - name: Test container
        run: |
          IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}
          podman run -d --name api -p 8000:8000 $IMAGE:$GITHUB_SHA
          sleep 5
          curl --fail http://localhost:8000/health
          podman rm -f api

      - name: Login to GHCR
        run: echo "${{ secrets.GITHUB_TOKEN }}" | podman login ghcr.io -u ${{ github.actor }} --password-stdin

      - name: Publish image
        run: |
          IMAGE=ghcr.io/${GITHUB_REPOSITORY,,}
          podman push $IMAGE:$GITHUB_SHA
```

### What the main parts mean

  Part                Meaning
  ------------------- -------------------------------------------------
  `on`                Events that trigger the workflow
  `push`              Runs when code is pushed to `main`
  `pull_request`      Runs tests for pull requests targeting `main`
  `jobs`              Groups of work
  `needs: test`       Build waits until tests pass
  `packages: write`   Permits publishing a package to GHCR
  `podman build`      Builds the image
  `podman run`        Starts a temporary container for a health check
  `podman push`       Uploads the image to GHCR
  `GITHUB_SHA`        Full commit ID used as the image tag

## 4. Commit and push

From PowerShell in your project folder, assuming Git is already
configured:

``` powershell
git add .
git commit -m "Add GitHub Actions CI and container publishing"
git push origin main
```

## 5. Verify the workflow

1.  Open the GitHub repository.
2.  Select **Actions**.
3.  Open the latest **FastAPI CI/CD** run.
4.  Confirm the `test` job succeeds.
5.  Confirm the `build` job succeeds, including **Test container** and
    **Publish image**.

Pull requests run the test job. With this YAML, the image is published
only after a push to `main` and successful tests.

## 6. Find the image and commit SHA

The workflow publishes an image in this format:

``` text
ghcr.io/OWNER/REPOSITORY:FULL_COMMIT_SHA
```

To find the SHA, open the successful workflow run and then open its
associated commit. Copy the full SHA. Alternatively, run this locally:

``` powershell
git rev-parse HEAD
```

The local SHA matches the published image only if your local `HEAD` is
the same commit that the successful workflow built.

**Important:** This workflow publishes a SHA-tagged image, not `latest`.
Use the full SHA when pulling the image on EC2.

## 7. GHCR public/private access

-   **Public package:** EC2 can normally pull it without logging in.
-   **Private package:** EC2 needs permission to read it. A common
    option is a GitHub classic personal access token with
    `read:packages` and access to the package. Organization SSO
    authorization may also be required.
-   Never commit or share tokens.

For a private package, log in using the same user context that will pull
the image. If you use `sudo podman pull`, use `sudo podman login` too:

``` bash
read -rsp "GitHub token: " GHCR_TOKEN
echo
printf '%s' "$GHCR_TOKEN" | sudo podman login ghcr.io \
  -u YOUR_GITHUB_USERNAME \
  --password-stdin
unset GHCR_TOKEN
```

Enter your token at the hidden prompt. Do not paste it into source code.
If login returns `403 Forbidden`, check token type, `read:packages`,
package permissions, organization SSO requirements, and username. For a
public package, try pulling without logging in.

# Part 2 --- Amazon EC2: Beginner Guide

## 1. What EC2 does in this project

-   GitHub stores the source code.
-   GitHub Actions tests the code and builds the image.
-   GHCR stores the image.
-   EC2 runs the image using Podman.
-   Your computer accesses the API through the EC2 public IPv4 address
    and an allowed port.

## 2. Select or create an EC2 instance

In the AWS Console:

1.  Open **EC2 → Instances**.
2.  Create a suitable learning instance or select your existing one.
3.  Ensure it has a public IPv4 address for direct internet access.
4.  Note its attached security group.
5.  Make sure you can connect to the instance, using EC2 Instance
    Connect or SSH.

For SSH, allow inbound TCP port `22` only from your own public IP when
possible. Keep your private key secure.

## 3. Install Podman and curl

On a compatible Amazon Linux instance:

``` bash
sudo dnf install -y podman curl
podman --version
curl --version
```

If `dnf` is not available, check your operating system and use its
appropriate package manager.

## 4. Pull the published image

Replace the placeholders with your actual GitHub owner, repository, and
full commit SHA:

``` bash
sudo podman pull ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud:FULL_COMMIT_SHA
```

Use the same repository name as the workflow, in lowercase. If the
package is private, log in first using the GHCR instructions in Part 1.
Do not use `latest` unless the workflow has been changed to publish that
tag.

## 5. Run the container

``` bash
sudo podman run -d \
  --name fastapi-crud \
  --restart=always \
  -p 8000:8000 \
  ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud:FULL_COMMIT_SHA
```

Replace the image placeholders. If a container named `fastapi-crud`
already exists and you intend to replace it, remove it first:

``` bash
sudo podman rm -f fastapi-crud
```

Only remove it if you are sure you no longer need that container.

Check status and logs:

``` bash
sudo podman ps
sudo podman logs fastapi-crud
```

`--restart=always` is useful, but should not be treated as a guarantee
of startup after every host reboot in every Podman setup. For reliable
boot-time startup, use a systemd service or Podman's Quadlet and test it
after reboot.

## 6. Test the API from EC2

Run these commands on the EC2 instance:

``` bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

Expected health response:

``` json
{"status":"ok"}
```

If these fail, inspect the container logs and port mapping before
troubleshooting AWS networking.

# Part 3 --- Port Configuration

## 1. How the port mapping works

The FastAPI application listens on port `8000` inside the container. The
Podman option `-p HOST_PORT:CONTAINER_PORT` publishes a container port
on the EC2 host.

``` text
Your browser
    |
    | http://EC2_PUBLIC_IP:8000
    v
EC2 security group (allows TCP 8000)
    |
    v
EC2 host port 8000
    |
    | Podman -p 8000:8000
    v
Container port 8000
    |
    v
FastAPI / Uvicorn
```

The first number in `-p 8000:8000` is the EC2 host port. The second
number is the port inside the container.

## 2. Ports used in this project

  ------------------------------------------------------------------------
  Location                                      Port Purpose
  --------------------- ---------------------------- ---------------------
  Uvicorn inside                              `8000` FastAPI listens here
  container                                          

  Podman mapping                         `8000:8000` Maps EC2 port 8000 to
                                                     container port 8000

  EC2 security group                      TCP `8000` Allows inbound API
                                                     traffic

  SSH, if used                              TCP `22` Remote administration
  ------------------------------------------------------------------------

The container's listening port, Podman's published port, and the
security group's inbound port must be consistent.

## 3. Configure the EC2 security group

In the AWS Console:

1.  Open **EC2 → Instances** and select the instance.
2.  Select **Security**.
3.  Open the attached security group.
4.  Select **Edit inbound rules**.
5.  Add this rule:

  Field        Value
  ------------ -----------------------------------
  Type         Custom TCP
  Protocol     TCP
  Port range   `8000`
  Source       Your public IP address with `/32`

For example, `203.0.113.25/32` illustrates the format; it is not your
actual IP. Use your current public IP. Restrict the port to your IP for
this learning demo rather than opening it to everyone.

A public IPv4 address alone is not sufficient. The security group and
network routing must also permit the traffic.

## 4. Access the API from your computer

Find the current **Public IPv4 address** in the EC2 Console. Replace
`EC2_PUBLIC_IP` below:

``` text
http://EC2_PUBLIC_IP:8000/
http://EC2_PUBLIC_IP:8000/health
http://EC2_PUBLIC_IP:8000/docs
```

-   `/` checks the root endpoint.
-   `/health` checks the service.
-   `/docs` opens interactive Swagger documentation.

These URLs use HTTP without TLS. Use them only for a restricted demo,
not a production service.

## 5. Use a different external port (optional)

You can publish EC2 port `8080` while the app continues listening on
container port `8000`:

``` bash
sudo podman run -d \
  --name fastapi-crud \
  -p 8080:8000 \
  ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud:FULL_COMMIT_SHA
```

In this example:

-   EC2 host port: `8080`
-   Container port: `8000`
-   Security group inbound rule: TCP `8080`, restricted to your IP
-   URL: `http://EC2_PUBLIC_IP:8080/health`

The first port in the Podman mapping must match the security-group port.
The second must match the port on which the app listens inside the
container.

## 6. Troubleshooting checklist

If the API works on EC2 but not from your computer, check these items in
order:

1.  Container is running:

    ``` bash
    sudo podman ps
    ```

2.  Port mapping resembles `0.0.0.0:8000->8000/tcp`.

3.  Local health check succeeds:

    ``` bash
    curl http://localhost:8000/health
    ```

4.  Inspect logs:

    ``` bash
    sudo podman logs fastapi-crud
    ```

5.  Security group allows inbound TCP `8000` from your current public
    IP.

6.  You are using the instance's current public IPv4 address.

7.  The instance's network has appropriate routing to an internet
    gateway for inbound internet access.

8.  The GHCR owner, repository, tag, package visibility, and permissions
    are correct.

## 7. Basic security recommendations

-   Restrict inbound port `8000` to your IP for a learning demo.
-   Never expose GitHub tokens or AWS private keys.
-   Do not commit credentials to GitHub.
-   Plain HTTP is not suitable for production.
-   For production, use HTTPS through a properly configured reverse
    proxy or load balancer, apply suitable authentication and
    authorization, and use persistent storage such as a database.
-   Review AWS costs and stop or terminate resources you no longer need.

# Quick Reference

## GitHub Actions

-   Workflow: `.github/workflows/ci-cd.yml`
-   Results: repository → **Actions**
-   Image: `ghcr.io/OWNER/REPOSITORY:FULL_COMMIT_SHA`
-   This workflow publishes the image after successful tests on a push
    to `main`; it does not deploy to EC2.

## EC2 commands

``` bash
sudo dnf install -y podman curl
sudo podman pull ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud:FULL_COMMIT_SHA
sudo podman run -d --name fastapi-crud --restart=always -p 8000:8000 ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud:FULL_COMMIT_SHA
sudo podman ps
curl http://localhost:8000/health
```

## Port mapping

``` text
-p EC2_HOST_PORT:CONTAINER_PORT
-p 8000:8000
```

For browser access, allow inbound TCP `8000` in the EC2 security group
and visit:

``` text
http://EC2_PUBLIC_IP:8000/docs
```

**End of manual.**
