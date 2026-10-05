import numpy as np
import matplotlib.pyplot as plt
import matplotlib
import panel as pn

matplotlib.use('agg')  # Use non-GUI backend

pn.extension()

# Data
x = np.linspace(0, 10, 500)

# Function to create the plot
def plot(freq=1.0, amp=1.0, wave_type='sin'):
    fig, ax = plt.subplots(figsize=(6, 4))
    if wave_type == 'sin':
        y = amp * np.sin(freq * x)
    else:
        y = amp * np.cos(freq * x)
    
    ax.plot(x, y, lw=2)
    ax.set_title(f"{wave_type.title()} Wave - Freq: {freq}, Amp: {amp}")
    ax.set_ylim(-5, 5)
    ax.grid(True)
    plt.close(fig)  # Prevent double display
    return fig

# Interactive widgets
freq_slider = pn.widgets.FloatSlider(name='Frequency', start=0.1, end=5.0, step=0.1, value=1.0)
amp_slider = pn.widgets.FloatSlider(name='Amplitude', start=0.1, end=5.0, step=0.1, value=1.0)
wave_selector = pn.widgets.RadioButtonGroup(name='Function', options=['sin', 'cos'], button_type='success')

# Dashboard layout
dashboard = pn.Column(
    "# 📊 Matplotlib Interactive Dashboard",
    pn.Row(freq_slider, amp_slider, wave_selector),
    pn.bind(plot, freq=freq_slider, amp=amp_slider, wave_type=wave_selector)
)

# Serve dashboard
dashboard.servable()
