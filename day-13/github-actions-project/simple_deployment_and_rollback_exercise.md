# Simple Deployment and Rollback Exercise

## Objective

Use one simple Python script, `deploy_container_simple.py`, to deploy a
new FastAPI container version and roll back to an earlier stable version
on EC2.

The script pulls the selected image from GitHub Container Registry
(GHCR), removes the existing container, and starts the selected version.

-   **Deploy:** use the new version's commit SHA.
-   **Rollback:** use the previous stable version's commit SHA.

## Prerequisites

-   `deploy_container_simple.py` is available on the EC2 instance.
-   Podman is installed.
-   GitHub Actions has successfully published both images to GHCR.
-   You know the full commit SHA for Version 1 and Version 2.
-   For a private GHCR package, you are authenticated with
    `sudo podman login ghcr.io`.

The examples use port mapping `8000:8000`.

------------------------------------------------------------------------

## 1. Deploy Version 2

Run on EC2:

``` bash
sudo python3 deploy_container_simple.py \
  --image ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud \
  --tag V2_COMMIT_SHA
```

Replace:

-   `YOUR_GITHUB_USERNAME` with your GitHub username or organization.
-   `V2_COMMIT_SHA` with the **full commit SHA** of the published
    Version 2 image.

Verify the deployment:

``` bash
curl http://localhost:8000/
curl http://localhost:8000/health
sudo podman ps
```

If you changed the root endpoint for Version 2, the first command should
show the new response. The health endpoint should return:

``` json
{"status":"ok"}
```

## 2. Roll back to Version 1

If Version 2 is faulty, run the same script using the full SHA of the
previously published stable image:

``` bash
sudo python3 deploy_container_simple.py \
  --image ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud \
  --tag V1_COMMIT_SHA
```

Replace `V1_COMMIT_SHA` with the full commit SHA of Version 1.

Verify the rollback:

``` bash
curl http://localhost:8000/
curl http://localhost:8000/health
sudo podman ps
```

The root endpoint should now show the original Version 1 response, and
the health endpoint should return:

``` json
{"status":"ok"}
```

------------------------------------------------------------------------

## 3. Demonstration summary

  Action               Image tag         Expected result
  -------------------- ----------------- ----------------------
  Deploy new version   `V2_COMMIT_SHA`   Version 2 runs
  Roll back            `V1_COMMIT_SHA`   Version 1 runs again

Both images must already have been published to GHCR by GitHub Actions.
The current workflow uses full commit SHA tags; do not use `latest`
unless you have modified the workflow to publish that tag.

## Important notes

-   This is a **manual deployment and rollback** exercise. The script
    does not automatically detect a bad release or roll back on its own.
-   The script removes the existing container before starting the
    selected version. There may be a brief interruption.
-   The starter FastAPI application stores product data in memory.
    Replacing the container loses those records.
-   For a private GHCR package, authenticate first using
    `sudo podman login ghcr.io`.
-   Ensure the EC2 security group allows inbound TCP port `8000` from
    your public IP if you need to access the API from your computer.
-   Do not expose GitHub tokens or other credentials in source code.

## Quick reference

Deploy Version 2:

``` bash
sudo python3 deploy_container_simple.py --image ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud --tag V2_COMMIT_SHA
```

Roll back to Version 1:

``` bash
sudo python3 deploy_container_simple.py --image ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud --tag V1_COMMIT_SHA
```

**Exercise complete:** the same script deploys either version, depending
on the image tag supplied.
