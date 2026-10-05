import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

# Data
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Create figure & axis
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.3)  # Leave space for sliders
line, = ax.plot(x, y, lw=2)
ax.set_ylim(-5, 5)
ax.set_title("Interactive Sine Wave (Matplotlib Slider)")
ax.grid(True)

# Slider Axes (position in figure coordinates)
ax_freq = plt.axes([0.2, 0.15, 0.65, 0.03])
ax_amp = plt.axes([0.2, 0.05, 0.65, 0.03])

# Sliders
slider_freq = Slider(ax_freq, 'Frequency', 0.1, 5.0, valinit=1.0, valstep=0.1)
slider_amp = Slider(ax_amp, 'Amplitude', 0.1, 5.0, valinit=1.0, valstep=0.1)

# Update function
def update(val):
    freq = slider_freq.val
    amp = slider_amp.val
    line.set_ydata(amp * np.sin(freq * x))
    fig.canvas.draw_idle()

# Connect sliders to update function
slider_freq.on_changed(update)
slider_amp.on_changed(update)

plt.show()
