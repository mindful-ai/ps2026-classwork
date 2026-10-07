import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
import pickle
import os

# Load dataset
df = pd.read_csv("heart.csv")

# Rename columns to match code expectations
df = df.rename(columns={
    "Age": "age",
    "Sex": "sex",
    "ChestPain": "cp",
    "RestBP": "trestbps",
    "Chol": "chol",
    "Fbs": "fbs",
    "RestECG": "restecg",
    "MaxHR": "thalach",
    "ExAng": "exang",
    "Oldpeak": "oldpeak",
    "Slope": "slope",
    "Ca": "ca",
    "Thal": "thal",
    "AHD": "target"
})

# Encode categorical columns
df["cp"] = df["cp"].map({"typical": 0, "asymptomatic": 1, "nonanginal": 2, "nontypical": 3})
df["thal"] = df["thal"].map({"normal": 1, "fixed": 2, "reversable": 3})
df["target"] = df["target"].map({"No": 0, "Yes": 1})
df = df.dropna()

# Features & target
X = df.drop(["target", "index"], axis=1)
y = df["target"]

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build pipeline
pipeline = Pipeline([
    ("scaler", StandardScaler()),
    ("clf", LogisticRegression(max_iter=1000))
])

# Train model
pipeline.fit(X_train, y_train)

# Evaluate
print("Train Accuracy:", pipeline.score(X_train, y_train))
print("Test Accuracy:", pipeline.score(X_test, y_test))

# Save model
os.makedirs("artifacts", exist_ok=True)
with open("artifacts/heart_pipeline.pkl", "wb") as f:
    pickle.dump(pipeline, f)

print("✅ Model saved to artifacts/heart_pipeline.pkl")
