# Reading of Fig. 3A: aortic flow, pulmonary hypertension (red dash-dot line), first plotted cycle. Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 1, 2], "y_vals": [0, 200, 400, 600], "color": "red", "on_axis": True})
