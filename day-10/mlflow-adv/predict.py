
import mlflow
import mlflow.sklearn
import pandas as pd

mlflow.set_tracking_uri("http://localhost:5000")

# Load the model registered with the champion alias
model_uri = "models:/IrisClassifier@champion"
model = mlflow.sklearn.load_model(model_uri)

# One sample: sepal length, sepal width,
# petal length, petal width (in cm)
sample = pd.DataFrame(
    [[5.1, 3.5, 1.4, 0.2]],
    columns=[
        "sepal length (cm)",
        "sepal width (cm)",
        "petal length (cm)",
        "petal width (cm)",
    ],
)

prediction = model.predict(sample)

print("Predicted class:", int(prediction[0]))
print("Predicted species:", ["setosa", "versicolor", "virginica"][int(prediction[0])])
