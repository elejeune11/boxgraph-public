"""Fig. 6, finite element local strain at A, eps_A, against Delta u2/l: the blue spheres (the legend marker is left out).

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.load(image, "6")
    return C.read_markers(image, cal, "blue", occluders=("red",))
