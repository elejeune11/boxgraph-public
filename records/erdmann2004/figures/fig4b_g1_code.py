"""Fig. 4(b), gamma = 1.0: the topmost line at N0 = 50 (gamma = 10 has left the plot).

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_curve(image, at, "4b", start_x=50.0, k=0)
