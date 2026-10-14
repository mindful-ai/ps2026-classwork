import argparse

import mlflow


def main():
    parser = argparse.ArgumentParser(
        description="Register a model logged by src.train"
    )
    parser.add_argument("--run-id", required=True, help="MLflow run ID")
    parser.add_argument(
        "--name",
        default="CustomerChurnModel",
        help="Registered model name",
    )
    args = parser.parse_args()

    model_uri = f"runs:/{args.run_id}/churn_model"
    registered = mlflow.register_model(
        model_uri=model_uri,
        name=args.name,
    )

    print(f"Registered model: {args.name}")
    print(f"Version: {registered.version}")
    print("Review quality-gate evidence and approval before deployment.")


if __name__ == "__main__":
    main()
