"""Fig. 3(d), deterministic N0 = 10: the dashes (separate blobs of 300-4000 px) linked into dashed lines; this is the line reaching furthest right (it bends down near tau = 3.2).

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_dashes(image, "3d", "right", 300, 4000)
