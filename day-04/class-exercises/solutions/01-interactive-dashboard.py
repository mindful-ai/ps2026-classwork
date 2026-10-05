import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import panel as pn
import matplotlib

matplotlib.use('agg')
# Panel setup
pn.extension()

# Load dataset
df = pd.read_csv(r"heart.csv")

# Filter Widgets
sex_filter = pn.widgets.RadioButtonGroup(name="Sex", options=["All", "Male", "Female"], button_type="primary")
cp_filter = pn.widgets.Select(name="Chest Pain Type", options=["All"] + sorted(df['ChestPain'].unique().tolist()))

# Function to apply filters
def filter_data(sex_choice, cp_choice):
    data = df.copy()
    if sex_choice == "Male":
        data = data[data['Sex'] == 1]
    elif sex_choice == "Female":
        data = data[data['Sex'] == 0]
    if cp_choice != "All":
        data = data[data['ChestPain'] == cp_choice]
    return data

# Plot function
def plot_dashboard(sex_choice, cp_choice):
    data = filter_data(sex_choice, cp_choice)
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))
    
    # 1: Age distribution
    axs[0, 0].hist(data['Age'], bins=10, color='skyblue', edgecolor='black')
    axs[0, 0].set_title("Age Distribution")
    axs[0, 0].grid(True)
    
    # 2: Cholesterol by target
    avg_chol = data.groupby('AHD')['Chol'].mean()
    axs[0, 1].bar(['No Disease', 'Disease'], avg_chol, color=['green', 'red'])
    axs[0, 1].set_title("Average Cholesterol by Heart Disease")
    axs[0, 1].grid(True)
    
    # 3: Resting BP distribution
    axs[1, 0].hist(data['RestBP'], bins=10, color='orange', edgecolor='black')
    axs[1, 0].set_title("Resting Blood Pressure Distribution")
    axs[1, 0].grid(True)
    
    # 4: Target count
    counts = data['AHD'].value_counts().sort_index()
    axs[1, 1].bar(['No Disease', 'Disease'], counts, color=['green', 'red'])
    axs[1, 1].set_title("Heart Disease Cases")
    axs[1, 1].grid(True)
    
    plt.tight_layout()
    plt.close(fig)
    return fig

# Bind function to widgets
dashboard = pn.Column(
    "# ❤️ Heart Disease Interactive Dashboard (Matplotlib + Panel)",
    pn.Row(sex_filter, cp_filter),
    pn.bind(plot_dashboard, sex_choice=sex_filter, cp_choice=cp_filter)
)

# Show in Jupyter or as standalone app
# dashboard

# To serve as a web app, uncomment:
dashboard.servable()
