"""Fig. 3, the N = 8 shape at the troughs: the troughs are nested, N = 2 deepest; N = 8 is run 3 from the bottom.

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    return len(runs) - 1 - 3 if len(runs) >= 5 else None


def read(image, at):
    cal = C.load(image, "3")
    return C.read_runs(image, cal, at, pick, r_range=(-1.40, 0.3), note="run 3 from the bottom in the trough")
