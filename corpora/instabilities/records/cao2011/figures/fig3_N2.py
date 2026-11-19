"""Fig. 3, the N = 2 shape: the outermost curve (highest at the crests, lowest in the troughs).

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    if not runs:
        return None
    top, bot = Y.value(runs[0][0]), Y.value(runs[-1][0])
    if top > 0.25:
        return 0
    if bot < -0.65:
        return len(runs) - 1
    return None


def read(image, at):
    cal = C.load(image, "3")
    # above the x-axis tick marks (which reach y = -1.44)
    return C.read_runs(image, cal, at, pick, r_range=(-1.40, 0.95), note="the outermost curve")
