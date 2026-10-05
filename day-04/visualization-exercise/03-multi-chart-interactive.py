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

# Function to generate different charts
def plot(chart_type='Line', freq=1.0, amp=1.0):
    fig, ax = plt.subplots(figsize=(6, 4))
    
    if chart_type == 'Line':
        y = amp * np.sin(freq * x)
        ax.plot(x, y, lw=2, color='blue')
        ax.set_title(f"Line Plot (Sine) - Freq: {freq}, Amp: {amp}")
        ax.set_ylim(-5, 5)
    
    elif chart_type == 'Bar':
        bins = np.linspace(-3, 3, 10)
        counts, edges = np.histogram(random_data, bins=bins)
        ax.bar(edges[:-1], counts, width=0.5, align='edge', color='orange', edgecolor='black')
        ax.set_title("Bar Chart of Random Data")
    
    elif chart_type == 'Histogram':
        ax.hist(random_data, bins=20, color='green', alpha=0.7, edgecolor='black')
        ax.set_title("Histogram of Random Data")
    
    ax.grid(True)
    plt.close(fig)  # Prevents duplicate display in notebooks
    return fig

# Widgets
chart_type_selector = pn.widgets.RadioButtonGroup(name='Chart Type', options=['Line', 'Bar', 'Histogram'], button_type='primary')
freq_slider = pn.widgets.FloatSlider(name='Frequency', start=0.1, end=5.0, step=0.1, value=1.0)
amp_slider = pn.widgets.FloatSlider(name='Amplitude', start=0.1, end=5.0, step=0.1, value=1.0)

# Show/Hide sliders dynamically (only for Line chart)
@pn.depends(chart_type_selector)
def slider_visibility(chart_type):
    if chart_type == 'Line':
        return pn.Row(freq_slider, amp_slider)
    else:
        return pn.pane.Markdown("No parameters for this chart type.")

# Dashboard Layout
dashboard = pn.Column(
    "# 📊 Multi-Chart Interactive Dashboard (Matplotlib)",
    pn.Row(chart_type_selector),
    slider_visibility,
    pn.bind(plot, chart_type=chart_type_selector, freq=freq_slider, amp=amp_slider)
)

# For Jupyter Notebook: just display `dashboard`
# dashboard

# For standalone web app:
dashboard.servable()
