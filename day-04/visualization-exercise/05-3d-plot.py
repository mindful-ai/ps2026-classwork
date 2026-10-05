'''

We can, for example, show Age vs Cholesterol vs Maximum Heart Rate colored by whether the person has heart disease or not.
This gives a sense of how these three variables interact in a 3D space.

'''

import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load dataset
df = pd.read_csv("heart.csv")  # replace with actual file name

# Optional: clean up column names if needed
df.columns = df.columns.str.strip()

# Map target column to colors
color_map = {'Yes': 'red', 'No': 'green'}
colors = df['AHD'].map(color_map)

# Create 3D plot
fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

sc = ax.scatter(df['Age'], df['Chol'], df['MaxHR'],
                c=colors,
                s=50, alpha=0.7, edgecolors='w')

ax.set_xlabel('Age', labelpad=10)
ax.set_ylabel('Cholesterol', labelpad=10)
ax.set_zlabel('Max Heart Rate', labelpad=10)
ax.set_title('Heart Disease Risk Factors in 3D', pad=20)

# Create legend manually
for label, color in color_map.items():
    ax.scatter([], [], [], c=color, label=label, s=50)
ax.legend(title='Heart Disease')

plt.show()


'''

Context:

X-axis → Age
Y-axis → Cholesterol level
Z-axis → Maximum heart rate achieved (thalach)

Color → Whether the patient has heart disease or not (target)

This visualization is useful to see if there’s a visual separation 
between patients with and without heart disease based on these three health indicators.

'''