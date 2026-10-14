
import os
import time
import mlflow

# 1. Configure the tracking database
mlflow.set_tracking_uri("sqlite:///mlflow.db")

# 2. Create or select an experiment
mlflow.set_experiment("Fresh MLflow Demo")


def calculate_metric(a, b):
    return a**2 + b**2


def main():
    param1 = 5
    param2 = 10

    # 3. Start an MLflow run
    with mlflow.start_run():
        # Log parameters
        mlflow.log_param("param1", param1)
        mlflow.log_param("param2", param2)

        # Calculate and log a metric
        metric = calculate_metric(param1, param2)
        mlflow.log_metric("calculated_metric", metric)

        # Log a tag
        mlflow.set_tag("version", "1.0")

        # Create and log an artifact
        os.makedirs("artifacts", exist_ok=True)

        artifact_path = "artifacts/run_info.txt"

        with open(artifact_path, "w", encoding="utf-8") as file:
            file.write(f"Parameters: {param1}, {param2}\n")
            file.write(f"Metric: {metric}\n")
            file.write(f"Timestamp: {time.asctime()}\n")

        mlflow.log_artifact(artifact_path)

        print("MLflow run completed successfully!")
        print(f"Parameters: {param1}, {param2}")
        print(f"Metric: {metric}")
        print(f"Run ID: {mlflow.active_run().info.run_id}")


if __name__ == "__main__":
    main()
