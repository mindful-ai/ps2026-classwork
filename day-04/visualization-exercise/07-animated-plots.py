import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Load your heart dataset
# Replace 'heart.csv' with your dataset path
df = pd.read_csv('heart.csv')

# Ensure target variable is string for coloring
df['AHD'] = df['AHD'].astype(str)

# Unique target classes
classes = df['AHD'].unique()
colors = {'Yes': 'red', 'No': 'green'}  # Assuming Yes = heart disease, No = healthy

# Create figure
fig, ax = plt.subplots()
sc = ax.scatter([], [], c=[], s=60, alpha=0.7, edgecolor='k')

ax.set_xlim(df['Age'].min() - 2, df['Age'].max() + 2)
ax.set_ylim(df['Chol'].min() - 10, df['Chol'].max() + 10)
ax.set_xlabel("Age")
ax.set_ylabel("Cholesterol")
ax.set_title("Animated Heart Dataset: Age vs Cholesterol")

# Update function for animation
def update(frame):
    # Select rows up to the current frame
    current_df = df.iloc[:frame+1]
    x = current_df['Age']
    y = current_df['Chol']
    c = [colors[val] for val in current_df['AHD']]
    
    sc.set_offsets(list(zip(x, y)))
    sc.set_color(c)
    return sc,

# Create animation
ani = animation.FuncAnimation(fig, update, frames=len(df), interval=100, blit=True, repeat=False)

plt.show()
