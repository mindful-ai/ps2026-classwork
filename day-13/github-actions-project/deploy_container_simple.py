#!/usr/bin/env python3
"""Simple deployment script for the FastAPI container on EC2.

Example:
    sudo python3 deploy_container.py \
      --image ghcr.io/YOUR_GITHUB_USERNAME/fastapi-podman-crud \
      --tag YOUR_FULL_COMMIT_SHA
"""

import argparse
import subprocess
import sys


def run(command):
    print("$", " ".join(command))
    subprocess.run(command, check=True)


def main():
    parser = argparse.ArgumentParser(description="Deploy a FastAPI container with Podman.")
    parser.add_argument("--image", required=True, help="GHCR image path")
    parser.add_argument("--tag", required=True, help="Image tag, usually the full commit SHA")
    args = parser.parse_args()

    image = f"{args.image}:{args.tag}"

    try:
        print(f"Pulling image: {image}")
        run(["podman", "pull", image])

        print("Removing the old container if it exists...")
        subprocess.run(
            ["podman", "rm", "-f", "fastapi-crud"],
            check=False,
        )

        print("Starting the container...")
        run([
            "podman", "run", "-d",
            "--name", "fastapi-crud",
            "--restart=always",
            "-p", "8000:8000",
            image,
        ])

        print("\nDeployment completed.")
        print("Check status: sudo podman ps")
        print("Test health:  curl http://localhost:8000/health")
        print("API docs:     http://EC2_PUBLIC_IP:8000/docs")

    except subprocess.CalledProcessError as error:
        print(f"Deployment failed (exit code {error.returncode}).")
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
