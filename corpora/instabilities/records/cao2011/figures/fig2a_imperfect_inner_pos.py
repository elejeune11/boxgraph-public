"""Fig. 2(a), imperfect path with a positive imperfection, the inner arm of the fold (the nearly flat curve just above zero).

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    pos = [i for i, r in enumerate(runs) if Y.value(r[0]) > 0.0005 and 4.5 <= r[1] <= 8]
    return pos[-1] if len(pos) >= 3 else None


def read(image, at):
    cal = C.load(image, "2a")
    return C.read_runs(image, cal, at, pick, note="lowest run above zero")
