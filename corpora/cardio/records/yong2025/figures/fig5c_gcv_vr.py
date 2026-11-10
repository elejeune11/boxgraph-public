# Reading of Fig. 5C: great cardiac vein flow, VR model (no IMP) (green line). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [0.5, 1.0, 1.5, 2.0], "color": "green"})
