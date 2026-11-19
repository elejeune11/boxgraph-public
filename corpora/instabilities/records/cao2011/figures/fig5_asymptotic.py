"""Fig. 5, the solid line 'analytical solution based on 6-mode approximation'.

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def start(runs, Y):
    # at x = 0.026 the line is the only black run between y = 0.215 and 0.445 (the text and
    # the arrows are further left)
    return 0


def read(image, at):
    cal = C.load(image, "5")
    return C.read_traced(image, cal, at, 0.026, start, r_range=(0.215, 0.445), note="the solid black line")
