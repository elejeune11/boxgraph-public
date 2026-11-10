# Reading of Fig. 6C: in vivo GCV waveform (purple dashed line) read on the left 'Simulated flow' axis: the measurement as the paper rescaled it to the models' stroke volume. Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [-2, 0, 2, 4, 6], "color": "purple"})
