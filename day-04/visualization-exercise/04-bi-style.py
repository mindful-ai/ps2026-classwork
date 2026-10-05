import numpy as np
import matplotlib.pyplot as plt
import panel as pn
import matplotlib

matplotlib.use('agg')
pn.extension()

# Data
np.random.seed(42)
x = np.linspace(0, 10, 200)
random_data = np.random.randn(200)

# Function to plot multiple charts at once
def multi_plot(freq=1.0, amp=1.0, bins=20):
    fig, axs = plt.subplots(3, 1, figsize=(15, 4))  # <- change here for the layout
    
    # Line plot (Sine Wave)
    y = amp * np.sin(freq * x)
    axs[0].plot(x, y, lw=2, color='blue')
    axs[0].set_title(f"Sine Wave (Freq={freq}, Amp={amp})")
    axs[0].set_ylim(-5, 5)
    axs[0].grid(True)
    
    # Histogram
    axs[1].hist(random_data, bins=bins, color='green', alpha=0.7, edgecolor='black')
    axs[1].set_title(f"Histogram (Bins={bins})")
    axs[1].grid(True)
    
    # Bar chart of binned data
    bin_edges = np.linspace(-3, 3, bins)
    counts, edges = np.histogram(random_data, bins=bin_edges)
    axs[2].bar(edges[:-1], counts, width=edges[1]-edges[0], align='edge', color='orange', edgecolor='black')
    axs[2].set_title("Bar Chart from Histogram")
    axs[2].grid(True)
    
    plt.tight_layout()
    plt.close(fig)  # Prevents double display in notebooks
    return fig

# Widgets
freq_slider = pn.widgets.FloatSlider(name='Frequency', start=0.1, end=5.0, step=0.1, value=1.0)
amp_slider = pn.widgets.FloatSlider(name='Amplitude', start=0.1, end=5.0, step=0.1, value=1.0)
bins_slider = pn.widgets.IntSlider(name='Histogram Bins', start=5, end=50, step=1, value=20)

# Dashboard Layout
dashboard = pn.Column(
    "# 📊 Multi-Chart Matplotlib Dashboard",
    "Adjust the sliders to see all charts update in real-time.",
    pn.Row(freq_slider, amp_slider, bins_slider),
    pn.bind(multi_plot, freq=freq_slider, amp=amp_slider, bins=bins_slider)
)

# For Jupyter Notebook: display inline
# dashboard

# For standalone web app:
dashboard.servable()
