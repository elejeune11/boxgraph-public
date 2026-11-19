"""Fig. 4, the curve N = 2: the curves are ordered N = 2 (lowest) to 6 (highest), so N = 2 is run 4 from the top.

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    # the five curves are the five topmost runs, each one line thick (text and the x-axis ticks
    # lie below them)
    top = runs[:5]
    if len(top) == 5 and all(3.5 <= h <= 8 for _, h in top):
        return 4
    return None


def read(image, at):
    cal = C.load(image, "4")
    # below the axis title "lambda* - lambda_W" (y above about 0.170)
    return C.read_runs(image, cal, at, pick, r_range=(0.004, 0.1685),
                       note="run 4 from the top among the five curves")
