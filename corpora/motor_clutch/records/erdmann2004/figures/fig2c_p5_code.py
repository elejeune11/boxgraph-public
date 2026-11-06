"""Fig. 2(c), p5: the highest tilted plateau. Of the lines only (blobs of 20000 px or more, so the labels '(c)' and 'p5' drop out), the topmost at tau = 5, traced both ways across the p0 crossing.

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_curve(image, at, "2c", start_x=5.0, k=0, solid_min_area=20000)
