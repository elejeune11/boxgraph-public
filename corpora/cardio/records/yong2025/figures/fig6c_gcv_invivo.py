# Reading of Fig. 6C: in vivo GCV waveform (purple dashed 'Validation' line), read on the right axis (MR flow, corrected for CSA 17 mm2). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_curve  # noqa: E402


def read(image, at):
    return read_curve(image, at, **{"x_vals": [0, 0.5, 1.0], "y_vals": [-1, 0, 1, 2, 3], "color": "purple", "y_side": "right"})
