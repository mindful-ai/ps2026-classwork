"""
Exercise: Build an Interactive Heart Disease Dashboard
Using Matplotlib + Panel
---------------------------------------------------------------
Complete the TODO sections to make the dashboard functional.

"""

# =========================
# 📦 1. Import Libraries
# =========================
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import panel as pn
import matplotlib

# Set Matplotlib backend for Panel
matplotlib.use('agg')

# Initialize Panel extension (required for widgets)
pn.extension()

# =========================
# 📂 2. Load Dataset
# =========================
# TODO: Load 'heart.csv' into a DataFrame
# Example: df = pd.read_csv("heart.csv")
df = None  # <-- Replace None with your code


# =========================
# 🎛 3. Create Filter Widgets
# =========================
# TODO: Create a RadioButtonGroup for Sex filter
sex_filter = None  # Example: pn.widgets.RadioButtonGroup(...)

# TODO: Create a Select widget for Chest Pain Type filter
cp_filter = None  # Example: pn.widgets.Select(...)


# =========================
# 🔍 4. Define Data Filter Function
# =========================
def filter_data(sex_choice, cp_choice):
    """
    Filters the dataset based on user widget choices.

    Parameters:
    -----------
    sex_choice : str
        "All", "Male", or "Female"
    cp_choice : str
        "All" or one of the Chest Pain categories

    Returns:
    --------
    DataFrame : Filtered data
    """
    # TODO: Start with a copy of the DataFrame
    data = None  # Example: df.copy()

    # TODO: Filter by Sex
    # Hint: 'Sex' column is 1 for Male, 0 for Female

    # TODO: Filter by Chest Pain type

    return data


# =========================
# 📊 5. Define Dashboard Plot Function
# =========================
def plot_dashboard(sex_choice, cp_choice):
    """
    Creates a 2x2 dashboard of charts based on filtered data.
    """
    data = filter_data(sex_choice, cp_choice)

    # Create subplots
    fig, axs = plt.subplots(2, 2, figsize=(12, 8))

    # Chart 1: Age Distribution
    # TODO: Use axs[0, 0].hist() to plot Age

    # Chart 2: Average Cholesterol by Heart Disease Target
    # TODO: Use groupby + mean, then axs[0, 1].bar()

    # Chart 3: Resting Blood Pressure Distribution
    # TODO: Use axs[1, 0].hist() to plot RestBP

    # Chart 4: Heart Disease Case Counts
    # TODO: Use value_counts() and axs[1, 1].bar()

    # Styling and layout
    plt.tight_layout()
    plt.close(fig)
    return fig


# =========================
# 🖥 6. Create Panel Layout
# =========================
dashboard = pn.Column(
    "# ❤️ Heart Disease Interactive Dashboard (Matplotlib + Panel)",
    pn.Row(sex_filter, cp_filter),
    pn.bind(plot_dashboard, sex_choice=sex_filter, cp_choice=cp_filter)
)

# =========================
# 🚀 7. Run the App
# =========================
# If in Jupyter, display with:
# dashboard

# If running as a standalone web app:
dashboard.servable()
