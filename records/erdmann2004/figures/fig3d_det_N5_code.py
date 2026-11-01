"""Fig. 3(d), deterministic N0 = 5: the other dashed line (ending near tau = 2.7).

Calibration and tracing are in _axes.py (same folder); this file says which panel and
which curve.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("erdmann2004_axes", os.path.join(os.path.dirname(__file__), "_axes.py"))
A = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(A)


def read(image, at):
    return A.read_dashes(image, "3d", "second_right", 300, 4000)
