import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load dataset
df = pd.read_csv("heart.csv")

# Inspect the first few rows
print(df.head())

# 3D Plot: Age vs Cholesterol vs MaxHR colored by AHD
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

# Scatter plot
scatter = ax.scatter(
    df["Age"], 
    df["Chol"], 
    df["MaxHR"],
    c=df["AHD"].map({'Yes': 1, 'No': 0}),  # Encode Yes=1, No=0
    cmap='coolwarm',
    s=50,
    alpha=0.7
)

# Labels
ax.set_xlabel("Age")
ax.set_ylabel("Cholesterol")
ax.set_zlabel("Max Heart Rate")
ax.set_title("Heart Disease Analysis: Age vs Chol vs MaxHR")

# Legend
legend1 = ax.legend(*scatter.legend_elements(),
                    title="Heart Disease (AHD)")
ax.add_artist(legend1)

plt.show()
