"""Fig. 4(a), N0 = 10 000: the top solid line just inside the left frame (N0 = 1 ... 10 000 lower to upper).

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_curve(image, at, "4a", start="left", k=0)
