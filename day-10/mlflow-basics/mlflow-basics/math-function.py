import mlflow
import math
import matplotlib.pyplot as plt


mlflow.set_experiment("Simple-Math")


with mlflow.start_run() as run:
    # Example parameters
    base = 2
    exponent = 5
    mlflow.log_param("base", base)
    mlflow.log_param("exponent", exponent)


    # Compute a result and log as a metric
    result = math.pow(base, exponent)
    mlflow.log_metric("power_result", result)


    # Add a custom tag
    mlflow.set_tag("demo_type", "math_function")


    # Generate a simple plot artifact
    x = list(range(1, 11))
    y = [math.pow(base, i) for i in x]
    plt.plot(x, y, marker="o")
    plt.title(f"{base}^x growth")
    plt.xlabel("x")
    plt.ylabel("y")
    plot_path = "power_plot.png"
    plt.savefig(plot_path)
    plt.close()
    mlflow.log_artifact(plot_path)


    print("Run ID:", run.info.run_id)