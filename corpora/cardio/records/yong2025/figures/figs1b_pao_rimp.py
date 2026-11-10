# Reading of Supp. Fig. S1B: central aortic pressure Pa (black line, partly under the Pd lines), Rbar + IMP ('conventional') model. Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [50, 100, 150], "color": "black", "under": ["red", "blue", "green", "darkred"], "open_w": 5})
