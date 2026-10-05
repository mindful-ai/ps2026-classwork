'''
You can wrap a Matplotlib figure into a Panel or Voila app for deployment as a web-based dashboard.

Installation:
> pip install panel

'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import panel as pn

matplotlib.use('agg')  # This should be set -> matplotlib backend 

pn.extension()

# Data
x = np.linspace(0, 10, 500)

# Function to create the plot
def plot(freq=1.0, amp=1.0, func='sin'):
    fig, ax = plt.subplots(figsize=(6, 4))
    if func == 'sin':
        y = amp * np.sin(freq * x)
    else:
        y = amp * np.cos(freq * x)
    
    ax.plot(x, y, lw=2)
    ax.set_title(f"{func.title()} Wave - Freq: {freq}, Amp: {amp}")
    ax.set_ylim(-5, 5)
    ax.grid(True)
    plt.close(fig)  # Prevents double display in notebooks
    return fig

# Interactive panel
freq_slider = pn.widgets.FloatSlider(name='Frequency', start=0.1, end=5.0, step=0.1, value=1.0)
amp_slider = pn.widgets.FloatSlider(name='Amplitude', start=0.1, end=5.0, step=0.1, value=1.0)
func_selector = pn.widgets.RadioButtonGroup(name='Function', options=['sin', 'cos'], button_type='success')

dashboard = pn.Column(
    "# 📊 Matplotlib Interactive Dashboard",
    pn.Row(freq_slider, amp_slider, func_selector),
    pn.bind(plot, freq=freq_slider, amp=amp_slider, func=func_selector)
)

# For Jupyter Notebook: show dashboard inline
# dashboard

# For standalone web app:
dashboard.servable()

'''

NOTE:
To serve on a webpage, use:
> panel serve 02-plot-with-panel.py --show

'''