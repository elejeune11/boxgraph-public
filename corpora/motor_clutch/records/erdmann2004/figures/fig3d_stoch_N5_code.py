"""Fig. 3(d), stochastic N0 = 5: of the solid lines only, the lower one at tau = 1.5.

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_curve(image, at, "3d", start_x=1.5, k=1, solid_min_area=20000)
