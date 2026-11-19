"""Fig. 8, surface strain against X/l_C for l_C/l = 0.00144: the dark red hexagons.

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def read(image, at):
    cal = C.load(image, "8")
    return C.read_markers(image, cal, "red", occluders=("blue",), exclude_inset="green", exclude_labelled=False)
