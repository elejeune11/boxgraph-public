"""Fig. 2(a), the perfect path, upper line (xi_1 > 0), starting at the origin. Runs thinner or thicker than the curves (leaders, arrows, text) are not curves.

Calibration, run finding and marker finding are in _cao.py (same folder); this file says which
panel and which curve or marker colour.
"""
import importlib.util
import os

_spec = importlib.util.spec_from_file_location("cao2011_figs", os.path.join(os.path.dirname(__file__), "_cao.py"))
C = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(C)


def pick(runs, x, Y):
    pos = [i for i, r in enumerate(runs) if Y.value(r[0]) > 0.001 and 4.5 <= r[1] <= 8]
    if not pos:
        return None
    # before the fold (x < 0.035) it is the only curve above zero (labels and leaders lie above
    # it): the lowest positive run; after the fold it is the highest of the three curves, which
    # are the three lowest positive runs (text lies above them)
    if x < 0.035:
        return pos[-1]
    return pos[-3] if len(pos) >= 3 else None


def read(image, at):
    cal = C.load(image, "2a")
    return C.read_runs(image, cal, at, pick, note="perfect path, upper line")
