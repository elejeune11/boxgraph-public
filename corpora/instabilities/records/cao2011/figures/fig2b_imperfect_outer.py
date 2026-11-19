"""Fig. 2(b), the imperfect path, outer arm of the fold (the curve just above the perfect line).

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    c = [i for i, r in enumerate(runs) if r[1] >= 4.5 and Y.value(r[0]) < 0.0015]
    return c[-2] if len(c) >= 3 else None


def read(image, at):
    cal = C.load(image, "2b")
    return C.read_runs(image, cal, at, pick, r_range=(-0.0425, 0.004), note="second run from the bottom")
