# Reading of Fig. 2C: simulated RCA microvascular resistance Rmicro(t) (black line). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, None, None, None, None, 0.5, None, None, None, None, 1.0], "y_vals": [0, 50, 100, 150], "color": "black"})
