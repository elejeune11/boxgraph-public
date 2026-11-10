# Reading of Fig. 4E: LCX intramural arterial flow, VR + IMP ('new') model (red line). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [0, None, 1, None, 2], "color": "red"})
