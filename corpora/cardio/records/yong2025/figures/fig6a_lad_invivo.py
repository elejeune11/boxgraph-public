# Reading of Fig. 6A: in vivo LAD waveform (purple dashed 'Validation' line), read on the right axis (Doppler flow velocity). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [0, 10, 20, 30, 40, 50], "color": "purple", "y_side": "right"})
