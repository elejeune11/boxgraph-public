# Reading of Fig. 7C: LAD mean flow, whole bar height (grey bars; bars 1-4: Norm VR+IMP, PH VR+IMP, Norm Rbar+IMP, PH Rbar+IMP). Shared method in _wave.py.
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wave import read_bars  # noqa: E402


def read(image, at):
    return read_bars(image, at, **{"y_vals": [0, 0.5, 1.0, 1.5], "series": 0, "edge": "top"})
