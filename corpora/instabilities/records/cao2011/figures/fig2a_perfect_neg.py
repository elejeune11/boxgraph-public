"""Fig. 2(a), the perfect path, lower line (xi_1 < 0).

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    neg = [i for i, r in enumerate(runs) if Y.value(r[0]) < -0.001 and 4.5 <= r[1] <= 8]
    if not neg:
        return None
    # before the fold the only curve below zero: the highest negative run; after it the lowest
    # of the three highest negative runs (the axis title lies below them)
    if x < 0.035:
        return neg[0]
    return neg[2] if len(neg) >= 3 else None


def read(image, at):
    cal = C.load(image, "2a")
    return C.read_runs(image, cal, at, pick, r_range=(-0.0835, 0.1), note="perfect path, lower line")
